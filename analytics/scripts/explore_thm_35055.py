"""Read-only exploration for the thermal-behind-35055 task (Q1 schema orientation)."""
import awconnect
from awconnect import db

awconnect.configure("read_only")

print("=== DISTINCT ResourceType ===")
print(db.getDfFromAwDb("SELECT DISTINCT ResourceType FROM AW.dbo.isoErcotScedGen ORDER BY ResourceType"))

print("\n=== cpnode columns (TOP 1) ===")
print(db.getDfFromAwDb("SELECT TOP 1 * FROM AW.dbo.cpnode").T)

print("\n=== station table? TOP 1 ===")
try:
    print(db.getDfFromAwDb("SELECT TOP 1 * FROM AW.dbo.station").T)
except Exception as e:
    print("station err:", e)

print("\n=== row counts per shift vector (all rows, no threshold) ===")
for pid in (75138717, 87025608):
    q = f"""SELECT COUNT(*) AS n_rows, COUNT(DISTINCT ps.cpNodeId) AS n_cpnode
            FROM AW.dbo.psenShiftView ps WHERE ps.psenShiftID = {pid}"""
    print(pid, db.getDfFromAwDb(q).to_dict("records"))

print("\n=== psenShiftView columns (TOP 1) ===")
print(db.getDfFromAwDb("SELECT TOP 1 * FROM AW.dbo.psenShiftView WHERE psenShiftID=87025608").T)
