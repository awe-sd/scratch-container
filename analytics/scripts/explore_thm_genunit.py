"""Match behind-35055 thermal units to AW.DBO.GENUNIT (ISOMARKETID=6)."""
import awconnect
import pandas as pd
from awconnect import snowflake

awconnect.configure("read_only")
pd.set_option("display.max_columns", None); pd.set_option("display.width", 240)

names = ["SCES_UNIT1_J01","SCES_UNIT1_J02","SCES_UNIT1_J03","SCES_UNIT1_J04",
         "BOSQUESW_CC2_1","BOSQUESW_CC2_2","BOSQUESW_CC2_3","BOSQUESW_CC2_4",
         "PANDA_T1_CC1_1","PANDA_T1_CC1_2","PANDA_T2_CC1_1","PANDA_T2_CC1_2",
         "BOSQUESW_CC1_1","BOSQUESW_CC1_2"]
inlist = ",".join(f"'{n}'" for n in names)
cols = "SEGENDEVICENAME, UNITNAME, GENPLANTID, GENFUELTYPE, RESOURCE_TYPE, BUSNAME, SUMMERMW, NAMEPLATEMW, UNITOWNER, CPNODEID"
d = snowflake.performQuery(dbName="AW",
    sqlQuery=f"SELECT {cols} FROM AW.DBO.GENUNIT WHERE ISOMARKETID=6 AND SEGENDEVICENAME IN ({inlist}) ORDER BY SEGENDEVICENAME",
    warehouse=snowflake.READ_ONLY_WH)
print("matched by SEGENDEVICENAME:", len(d))
print(d.to_string())

# distinct GENFUELTYPE / RESOURCE_TYPE across all ERCOT thermal-relevant, sanity
print("\n=== distinct GENFUELTYPE (ERCOT) ===")
print(snowflake.performQuery(dbName="AW",
    sqlQuery="SELECT GENFUELTYPE, COUNT(*) n FROM AW.DBO.GENUNIT WHERE ISOMARKETID=6 GROUP BY GENFUELTYPE ORDER BY n DESC",
    warehouse=snowflake.READ_ONLY_WH).to_string())
