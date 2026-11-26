-- Append paths sinking BRANDON_RN to AWVAL.DBO.FwdAuctionDecompByPath (ptoID 1504).
-- Same generator as the original insert, with two changes:
--   1. The sink is hardcoded to BRANDON_RN (cpnodeid 56563, bus 59174, 12 kV) — it fails
--      the original >=69 kV node filter, so it is resolved in its own CTE without that filter.
--   2. ftr_pairs is replaced by brandon_pairs: every qualifying source (the same >=69 kV
--      universe as the original run) x the Brandon sink, with NO bus-distance <= 1.0
--      requirement. Distance is still attached via LEFT JOIN for reference.
-- Because ONLY sinkName = BRANDON_RN rows are produced, and no Brandon-sink rows exist
-- under ptoID 1504 today (verified 2026-08-12), this cannot duplicate existing paths.
-- Prereq: AWVAL.DBO.tmp_branch_constraints must exist in the session (same CREATE as before).

INSERT INTO AWVAL.DBO.FwdAuctionDecompByPath (
    ptoID, runDate, sourceName, sinkName, sourceBusNum, sourceBusKv, sinkBusNum, sinkBusKv,
    sourceCpNodeId, sinkCpNodeId, priceClassID, branchConstraintID, ftrConstraintID, direction,
    ftrMonitorID, monitored, contingency, priceMWH_mean, monitoredType, fromNum, toNum,
    sourceSF, sinkSF, pathSF, constraintContribution
)
SELECT 1504 as ptoID,
       CURRENT_TIMESTAMP as runDate,
       results.sourceName, results.sinkName, results.sourceBusNum, results.sourceBusKv,
       results.sinkBusNum, results.sinkBusKv, results.sourceCpNodeId, results.sinkCpNodeId,
       results.priceClassID, results.branchConstraintID, results.ftrConstraintID, results.direction,
       results.ftrMonitorID, results.monitored, results.contingency, results.priceMWH_mean,
       results.monitoredType, NULL as fromNum, NULL as toNum,
       results.sourceSF, results.sinkSF, results.pathSF, results.constraintContribution
FROM (

WITH bus_distances AS (
    SELECT source_bus_num, sink_bus_num, distance
    FROM AWVAL.DBO.BusDistanceMatrix
    WHERE ptoID = 1504 AND isoMarketID = 6
),

ftr_nodes AS (
    SELECT T1.name as ftrName, T1.cpnodeid, MAX(T2.BusKv) as maxBusKv
    FROM AW.dbo.cpnode T1
    LEFT JOIN AW.dbo.isoErcotCpnodeBus T2 ON T1.cpnodeid = T2.cpNodeID
    WHERE T1.isomarketid = 6 AND T1.ftrMarketValid = 1 AND T1.name IS NOT NULL
    GROUP BY T1.name, T1.cpnodeid
),

ftr_nodes_with_bus AS (
    SELECT fn.ftrName, fn.cpnodeid, IFNULL(fn.maxBusKv, 345) as BusKv, MIN(eb.BusNum) as BusNum
    FROM ftr_nodes fn
    LEFT JOIN AW.dbo.isoErcotCpnodeBus eb
        ON fn.cpnodeid = eb.cpNodeID AND fn.maxBusKv = eb.BusKv AND fn.maxBusKv >= 69
    GROUP BY fn.ftrName, fn.cpnodeid, fn.maxBusKv
    HAVING IFNULL(fn.maxBusKv, 345) >= 69
),

-- Brandon sink resolved WITHOUT the >=69 kV filter (its only bus is 12 kV)
brandon_sink AS (
    SELECT fn.ftrName, fn.cpnodeid, fn.maxBusKv as BusKv, MIN(eb.BusNum) as BusNum
    FROM ftr_nodes fn
    LEFT JOIN AW.dbo.isoErcotCpnodeBus eb
        ON fn.cpnodeid = eb.cpNodeID AND fn.maxBusKv = eb.BusKv
    WHERE fn.ftrName = 'BRANDON_RN'
    GROUP BY fn.ftrName, fn.cpnodeid, fn.maxBusKv
),

-- every qualifying source x Brandon sink; no distance gate, distance attached for reference
ftr_pairs AS (
    SELECT source.ftrName as sourceName, sink.ftrName as sinkName,
           source.BusNum as sourceBusNum, source.BusKv as sourceBusKv,
           sink.BusNum as sinkBusNum, sink.BusKv as sinkBusKv,
           source.cpnodeid as sourceCpNodeId, sink.cpnodeid as sinkCpNodeId,
           bd.distance as busDistance, 6 as priceClassID
    FROM ftr_nodes_with_bus source
    INNER JOIN brandon_sink sink ON source.ftrName <> sink.ftrName
    LEFT JOIN bus_distances bd
        ON source.BusNum = bd.source_bus_num AND sink.BusNum = bd.sink_bus_num
),
pair_nodes AS (
    SELECT sourceCpNodeId AS cpNodeId FROM ftr_pairs
    UNION
    SELECT sinkCpNodeId FROM ftr_pairs
),
all_auction_constraints AS (
    SELECT fsp.ftrBindingId as ftrBindingID, fsp.ftrConstraintID, fsp.ftrBidMarketId as ftrBidMarketID,
           fsp.ftrPeriodId as ftrPeriodID, fsp.monitoredType, fsp.monitored, fsp.ftrMonitorID,
           fsp.branchMonitoredID, fsp.contingency, fsp.ftrContingencyID,
           fsp.branchContingencyId as branchContingencyID, fsp.branchConstraintID, fsp.direction,
           fsp.className, fsp.priceclassid as priceClassID, fsp.spMWH AS priceMWH
    FROM AW.dbo.ftrResultSPView fsp
    INNER JOIN AWVAL.DBO.tmp_branch_constraints bc ON fsp.branchConstraintID = bc.branchConstraintID
    WHERE fsp.isomarketid = 6
      AND fsp.priceclassid = 6
      AND ((fsp.ftrBidMarketId = 626061 AND fsp.ftrIsoPeriodName = 'JUN_2026') OR (fsp.ftrBidMarketId = 626071 AND fsp.ftrIsoPeriodName = 'JUL_2026') OR (fsp.ftrBidMarketId = 626081 AND fsp.ftrIsoPeriodName = 'AUG_2026') OR (fsp.ftrBidMarketId = 626261 AND fsp.ftrIsoPeriodName = 'AUG_2026') OR (fsp.ftrBidMarketId = 626261 AND fsp.ftrIsoPeriodName = 'SEP_2026') OR (fsp.ftrBidMarketId = 626261 AND fsp.ftrIsoPeriodName = 'OCT_2026'))
),
base_historical_constraints AS (
    SELECT monitoredType, monitored, contingency, direction, priceClassID, branchConstraintID,
           ftrMonitorID, ftrConstraintID, AVG(priceMWH) as priceMWH_mean,
           MAX(ftrBindingID) as ftrBindingID, MAX(ftrBidMarketID) as ftrBidMarketID,
           MAX(ftrPeriodID) as ftrPeriodID
    FROM all_auction_constraints
    GROUP BY monitoredType, monitored, contingency, direction, priceClassID, branchConstraintID,
             ftrMonitorID, ftrConstraintID
),
historical_constraints AS (
    SELECT bhc.monitoredType, bhc.monitored, bhc.contingency, bhc.direction, bhc.priceClassID,
           bhc.branchConstraintID,
           COALESCE(cfas.EXPECTEDCLEARPRICE, bhc.priceMWH_mean) as priceMWH_mean,
           bhc.ftrBindingID, bhc.ftrMonitorID, bhc.ftrConstraintID, bhc.ftrBidMarketID, bhc.ftrPeriodID
    FROM base_historical_constraints bhc
    LEFT JOIN AWVAL.DBO.ConstFwdAuctionSP cfas
        ON bhc.ftrConstraintID = cfas.ftrConstraintID AND bhc.priceClassID = cfas.priceClassID
       AND cfas.ftrBidMarketID = 626091 AND cfas.ftrPeriodID = 626091
       AND cfas.EXPECTEDCLEARPRICE IS NOT NULL
    UNION ALL
    SELECT frdm.monitoredType, frdm.monitored, frde.contingency, frdm.direction, cfas.priceClassID,
           bciv.branchConstraintID,
           IFNULL(cfas.EXPECTEDCLEARPRICE, cfas.AUCTIONPRICEMEAN) as priceMWH_mean,
           NULL as ftrBindingID, frdc.ftrMonitorID, cfas.ftrConstraintID, cfas.ftrBidMarketID, cfas.ftrPeriodID
    FROM AWVAL.DBO.ConstFwdAuctionSP cfas
    LEFT JOIN AW.DBO.ftrResultDefConstraint as frdc ON frdc.ftrConstraintID = cfas.ftrConstraintID
    LEFT JOIN AW.DBO.ftrResultDefMonitor as frdm ON frdm.ftrMonitorID = frdc.ftrMonitorID
    LEFT JOIN AW.DBO.ftrResultDefContingency as frde ON frde.ftrContingencyID = frdc.ftrContingencyID
    LEFT JOIN AW.DBO.branchConstraint as bciv
        ON bciv.branchMonitoredID = frdm.branchMonitoredID
       AND bciv.branchContingencyID = frde.branchContingencyID
    WHERE cfas.EXPECTEDCLEARPRICE IS NOT NULL
      AND cfas.FTRCONSTRAINTID NOT IN (
            SELECT FTRCONSTRAINTID FROM base_historical_constraints WHERE FTRCONSTRAINTID IS NOT NULL)
      AND cfas.ftrBidMarketID = 626091 AND cfas.ftrPeriodID = 626091
      AND cfas.priceClassID = 6
),
shift_factors_base AS (
    SELECT DISTINCT psen.cpNodeId, psd.branchConstraintID, frdm.Direction as direction,
           frdm.ftrMonitorID, frdc.ftrConstraintID, frdm.MonitoredType as monitoredType,
           frdm.Monitored as monitored, frde.Contingency as contingency, psen.psen as psens
    FROM AW.dbo.psenShiftDef AS psd
    INNER JOIN AW.dbo.psenShift AS psen ON psd.psenShiftID = psen.psenShiftID
    INNER JOIN AWVAL.DBO.tmp_branch_constraints bc ON psd.branchConstraintID = bc.branchConstraintID
    INNER JOIN AWVAL.DBO.ConstFwdAuctionSP cfas ON cfas.psenShiftID = psd.psenShiftID
    INNER JOIN pair_nodes pn ON psen.cpNodeId = pn.cpNodeId
    LEFT JOIN AW.DBO.ftrResultDefConstraint as frdc ON frdc.ftrConstraintID = cfas.ftrConstraintID
    LEFT JOIN AW.DBO.ftrResultDefMonitor as frdm ON frdm.ftrMonitorID = frdc.ftrMonitorID
    LEFT JOIN AW.DBO.ftrResultDefContingency as frde ON frde.ftrContingencyID = frdc.ftrContingencyID
    LEFT JOIN AW.DBO.branchConstraint as bciv
        ON bciv.branchMonitoredID = frdm.branchMonitoredID
       AND bciv.branchContingencyID = frde.branchContingencyID
    WHERE psd.psenShiftTypeId = 15
      AND cfas.priceclassid = 6
      AND psd.ptoID = 1504
),
shift_factors_pairs AS (
    SELECT sf1.branchConstraintID, sf1.direction, sf1.ftrMonitorID, sf1.ftrConstraintID,
           sf1.monitoredType, sf1.monitored, sf1.contingency,
           sf1.cpNodeId as sourceCpNodeId, sf2.cpNodeId as sinkCpNodeId,
           sf1.psens as sourceSF, sf2.psens as sinkSF, (sf1.psens - sf2.psens) as pathSF,
           fp.sourceName, fp.sinkName, fp.sourceBusNum, fp.sourceBusKv,
           fp.sinkBusNum, fp.sinkBusKv, fp.busDistance, fp.priceClassID
    FROM ftr_pairs fp
    INNER JOIN shift_factors_base sf1 ON sf1.cpNodeId = fp.sourceCpNodeId
    INNER JOIN shift_factors_base sf2
        ON sf2.cpNodeId = fp.sinkCpNodeId
       AND sf1.branchConstraintID = sf2.branchConstraintID
       AND sf1.ftrConstraintID = sf2.ftrConstraintID
)
SELECT DISTINCT
    sfp.sourceName, sfp.sinkName, sfp.sourceBusNum, sfp.sourceBusKv,
    sfp.sinkBusNum, sfp.sinkBusKv, sfp.busDistance, sfp.priceClassID,
    sfp.sourceCpNodeId, sfp.sinkCpNodeId, sfp.sourceSF, sfp.sinkSF, sfp.pathSF,
    hc.branchConstraintID, hc.ftrConstraintID, hc.direction, hc.ftrMonitorID,
    hc.monitored, hc.contingency, hc.priceMWH_mean, hc.monitoredType,
    (hc.priceMWH_mean * sfp.pathSF) as constraintContribution
FROM shift_factors_pairs sfp
INNER JOIN historical_constraints hc
    ON sfp.branchConstraintID = hc.branchConstraintID
   AND sfp.ftrConstraintID = hc.ftrConstraintID
   AND sfp.ftrMonitorID = hc.ftrMonitorID
   AND sfp.direction = hc.direction

) as results
-- hard guarantee: only Brandon-sink rows can be inserted, and never a row that already exists
WHERE results.sinkName = 'BRANDON_RN'
  AND NOT EXISTS (
        SELECT 1 FROM AWVAL.DBO.FwdAuctionDecompByPath f
        WHERE f.ptoID = 1504
          AND f.sinkCpNodeId = results.sinkCpNodeId
          AND f.sourceCpNodeId = results.sourceCpNodeId
          AND f.priceClassID = results.priceClassID
          AND f.ftrConstraintID = results.ftrConstraintID
  )
;
