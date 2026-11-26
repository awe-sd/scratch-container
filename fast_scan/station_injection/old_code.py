import argparse
import datetime
import logging
import site
import sys
import os

import pandas as pd
from dateutil.relativedelta import relativedelta
from sqlalchemy import text

import AWLogging
import AWUtil

import AWSnowflakeUtil as sf

site.addsitedir("G:\Common\Jiachun\pythonProject\jguoPackage")

sys.path.insert(
    0,
    os.path.abspath(os.environ["AWEP_CODEDIR3"] + "/ISO/Ercot/util"),
)
from pandas_util import move_column_inplace  # noqa: E402


def getStationMW(startTime, endTime):
    logging.info("start getStationMW({},{})".format(startTime, endTime))
    logging.info("read branch flow from isoErcotSeBranchView")
    branchFlowSql = """
    SELECT [timeStamp], fromStationName, toStationName, fromMW, toMW
    FROM AW.dbo.isoErcotSeBranchView
    where
    [timeStamp] >= '{}'
    and [timeStamp] <= '{}'
    """.format(startTime, endTime)
    with AWUtil.AWAlchemyEngine().connect() as alqcn:
        branchFlowData = pd.read_sql(sql=branchFlowSql, con=alqcn)

    if branchFlowData.shape[0] <= 0:
        return None

    branchFlowData.loc[branchFlowData["fromStationName"].isna(), "fromStationName"] = (
        branchFlowData.loc[branchFlowData["fromStationName"].isna(), "toStationName"]
    )
    branchFlowData.loc[branchFlowData["toStationName"].isna(), "toStationName"] = (
        branchFlowData.loc[branchFlowData["toStationName"].isna(), "fromStationName"]
    )
    logging.info("branchFlowData size={}".format(branchFlowData.shape))

    fromData = branchFlowData.groupby(["timeStamp", "fromStationName"], as_index=False)[
        ["fromMW"]
    ].sum()
    toData = branchFlowData.groupby(["timeStamp", "toStationName"], as_index=False)[
        ["toMW"]
    ].sum()

    stationData = fromData.merge(
        toData,
        how="outer",
        left_on=["timeStamp", "fromStationName"],
        right_on=["timeStamp", "toStationName"],
    )
    logging.info("stationData size={}".format(stationData.shape))

    stationData.loc[stationData["fromStationName"].isna(), "fromStationName"] = (
        stationData.loc[stationData["fromStationName"].isna(), "toStationName"]
    )
    stationData.loc[stationData["toStationName"].isna(), "toStationName"] = (
        stationData.loc[stationData["toStationName"].isna(), "fromStationName"]
    )
    stationData.loc[stationData["fromMW"].isna(), "fromMW"] = 0
    stationData.loc[stationData["toMW"].isna(), "toMW"] = 0
    stationData["WithdrawMW"] = -stationData["fromMW"] - stationData["toMW"]

    stationData = stationData.rename(columns={"fromStationName": "NmmsStationCode"})
    del stationData["toStationName"]

    return stationData


def getGenMW(startDate, endDate):
    logging.info("start getGenMW({}, {})".format(startDate, endDate))

    startTime2 = datetime.datetime.strptime(startDate, "%Y-%m-%d")
    startTime2 = startTime2 + relativedelta(minutes=15)
    endTime2 = datetime.datetime.strptime(endDate, "%Y-%m-%d")
    endTime2 = endTime2 + relativedelta(days=1) + relativedelta(minutes=15)

    logging.info(
        "read TelemeteredOutput from isoErcotScedGenResourceView between {} and {}".format(
            startTime2, endTime2
        )
    )
    genMWSql = """
    SELECT [TimeStamp]
    , ResourceName, TelemeteredOutput
    FROM AW.dbo.isoErcotScedGenResourceView
    where [timeStamp] >= '{}'
    and [timeStamp] <= '{}'
    """.format(
        startTime2.strftime("%Y-%m-%d %H:%M"), endTime2.strftime("%Y-%m-%d %H:%M")
    )
    with AWUtil.AWAlchemyEngine().connect() as alqcn:
        genMWData = pd.read_sql(sql=genMWSql, con=alqcn)

    logging.info("read genName, trainName, stationName from ercotDampsseGnDef")
    genName2StationSql = """
    SELECT genName, trainName, stationName
    FROM AW.dbo.ercotDampsseGnDef T1 join AW.dbo.ercotDampsseStation T2 on T1.stationId=T2.ercotDampsseStationId 
    """
    with AWUtil.AWAlchemyEngine().connect() as alqcn:
        genName2StationData = pd.read_sql(sql=genName2StationSql, con=alqcn)
    genName2StationData.loc[genName2StationData["trainName"].isna(), "trainName"] = (
        genName2StationData.loc[genName2StationData["trainName"].isna(), "genName"]
    )

    pat = "(" + "|".join(genName2StationData["trainName"].unique()) + ")"
    genMWData["trainName"] = genMWData["ResourceName"].str.extract(pat, expand=False)
    genMWData = genMWData.merge(genName2StationData, on="trainName", how="left")
    genMWData.sort_values(
        by=["TimeStamp", "trainName", "TelemeteredOutput"], inplace=True
    )
    genMWData.drop_duplicates(
        subset=["TimeStamp", "trainName", "TelemeteredOutput"], inplace=True
    )

    return genMWData


def combineStationMW(stationMW, genMW):
    logging.info("start combineStationMW()")
    genMW["newTimeStamp"] = pd.to_datetime(genMW["TimeStamp"]).sub(
        pd.to_timedelta(0, unit="min")
    )
    a = (
        genMW.groupby(["newTimeStamp", "stationName"])["TelemeteredOutput"]
        .sum()
        .reset_index()
    )
    a["Date"] = a["newTimeStamp"].dt.date
    a["Hour"] = a["newTimeStamp"].dt.hour
    b = (
        a.groupby(["Date", "Hour", "stationName"])["TelemeteredOutput"]
        .mean()
        .reset_index()
    )
    b = b.rename(columns={"stationName": "NmmsStationCode"})

    stationMW["Date"] = stationMW["timeStamp"].dt.date
    stationMW["Hour"] = stationMW["timeStamp"].dt.hour
    c = (
        stationMW.groupby(["Date", "Hour", "NmmsStationCode"])["WithdrawMW"]
        .mean()
        .reset_index()
    )

    finalStationMW = pd.merge(c, b, on=["Date", "Hour", "NmmsStationCode"], how="outer")
    finalStationMW = finalStationMW.rename(columns={"TelemeteredOutput": "GenMW"})
    for col in reversed(["Date", "Hour", "NmmsStationCode", "GenMW", "WithdrawMW"]):
        move_column_inplace(finalStationMW, col, 0)

    return finalStationMW


def calculateStationMW(startDate, endDate):
    logging.info("calculateStationMW from {} to {}".format(startDate, endDate))
    endTime = datetime.datetime.strptime(endDate, "%Y-%m-%d")
    endTime = endTime + relativedelta(days=1) - relativedelta(seconds=1)
    stationMW = getStationMW(startDate, endTime.strftime("%Y-%m-%d %H:%M:%S"))
    if stationMW is None:
        logging.info("no stationMW from {} to {}, stop.".format(startDate, endDate))
        return

    date__format = "delete from AW.dbo.ercotStationLoad where [Date]>='{}' and [Date]<='{}'".format(
        startDate, endDate
    )
    logging.info(date__format)
    with AWUtil.AWAlchemyEngine().begin() as connection:
        connection.execute(text(date__format))

    # also delete from snowflake:
    try:
        sf.executeSQL(
            sql=f"""DELETE FROM AW.dbo.ercotStationLoad WHERE "Date" >= '{startDate}' AND "Date" <= '{endDate}'""",
            dbName="AW",
        )
    except Exception as e:
        logging.error(f"Error deleting from Snowflake table ercotStationLoad: {e}")

    genMW = getGenMW(startDate, endDate)
    finalStationMW = combineStationMW(stationMW, genMW)

    finalStationMW = finalStationMW.loc[
        (
            finalStationMW["Date"]
            >= datetime.datetime.strptime(startDate, "%Y-%m-%d").date()
        )
        & (
            finalStationMW["Date"]
            <= datetime.datetime.strptime(endDate, "%Y-%m-%d").date()
        )
    ].copy()

    finalStationMW["Date"] = finalStationMW["Date"].astype("string")
    finalStationMW["Hour"] = finalStationMW["Hour"].astype("int32")
    finalStationMW["NmmsStationCode"] = finalStationMW["NmmsStationCode"].astype(
        "string"
    )
    logging.info("New data # = {}".format(finalStationMW.shape[0]))
    finalStationMW = finalStationMW[
        ["Date", "Hour", "NmmsStationCode", "GenMW", "WithdrawMW"]
    ]
    finalStationMW = finalStationMW.sort_values(by=["Date", "Hour", "NmmsStationCode"])

    finalStationMW.drop_duplicates(
        subset=["Date", "Hour", "NmmsStationCode"], keep="last", inplace=True
    )
    AWUtil.dfInsertAlchemy(
        finalStationMW, "AW.dbo.ercotStationLoad", chunkSize=51200 * 6
    )

    # also update snowflake:
    try:
        # merge should not be necessary but just in case since snowflake 
        # does not enforce PKs
        sf.writeDF(df=finalStationMW, dbName="AW", dbTable="ercotStationLoad", doMerge=True)
    except Exception as e:
        logging.error(f"Error updating Snowflake table ercotStationLoad: {e}")

if __name__ == "__main__":
    """
    python %USERPROFILE%\code\appianwaycode3\ISO\Ercot\SCED_BranchFlow_2_Load\SCED_BranchFlow_2_Load_StationLevel_DB.py --startTime 2014-12-03 --endTime 2023-12-01
    """
    AWLogging.getLogger(
        logFmt="%(asctime)s %(levelname)s - %(message)s", email=False, cloudWatch=False
    )
    logging.info("Start")

    parser = argparse.ArgumentParser(description=sys.argv[0])
    parser.add_argument("--startTime", help="format: 2022-12-19", default=None)
    parser.add_argument("--endTime", help="format: 2022-12-19", default=None)
    args = parser.parse_args()
    logging.info(args)

    startTime = (
        args.startTime
        if args.startTime is not None
        else (datetime.date.today() - relativedelta(days=63)).strftime("%Y-%m-%d")
    )
    endTime = (
        args.endTime
        if args.endTime is not None
        else (datetime.date.today() - relativedelta(days=60)).strftime("%Y-%m-%d")
    )

    #
    startTime = datetime.datetime.strptime(startTime, "%Y-%m-%d")
    endTime = datetime.datetime.strptime(endTime, "%Y-%m-%d")

    logging.info(f"startime={startTime}, endTime={endTime}")

    currentDay = startTime
    while currentDay <= endTime:
        logging.info("currentDay={}".format(currentDay))
        calculateStationMW(
            currentDay.strftime("%Y-%m-%d"), currentDay.strftime("%Y-%m-%d")
        )
        currentDay = currentDay + relativedelta(days=1)

    logging.info("Finish")
