"""Connectivity smoke test: awconnect (read_only profile) -> Snowflake."""
import awconnect
from awconnect import snowflake

awconnect.configure("read_only")

SQL = "SELECT COUNT(*) AS ROW_COUNT FROM AWDEV.DBO.AWCONNECT_RO_TEST"

df = snowflake.performQuery("AWDEV", SQL, warehouse=snowflake.READ_ONLY_WH, logInfo=False)
print(df)
