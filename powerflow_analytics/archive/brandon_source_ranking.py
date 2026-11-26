import math
import awconnect
awconnect.configure('read_only')
from awconnect import db
import pandas as pd

SINK = 56563  # BRANDON_RN cpnodeid
FTR_BID_MARKET = 626261
PRICE_DATE = '2026-09-01'
MARK_TYPE = 5  # auction decomposition (widest coverage)

# 1. price data, priceClass 2 (OnPeak) and 6 (OffPeak)
price = db.getDfFromAwDb(f'''
SELECT sourcecpNodeId, priceClassId, priceMWH
FROM AW.dbo.ftrOptionPriceMark
WHERE isomarketid=6 AND sinkcpNodeId={SINK} AND ftrBidMarketId={FTR_BID_MARKET}
  AND priceDate='{PRICE_DATE}' AND markTypeId={MARK_TYPE} AND priceClassId IN (2,6)
''')
onpeak = price[price.priceClassId == 2][['sourcecpNodeId', 'priceMWH']].rename(columns={'priceMWH': 'price_onpeak'})
offpeak = price[price.priceClassId == 6][['sourcecpNodeId', 'priceMWH']].rename(columns={'priceMWH': 'price_offpeak'})
merged = onpeak.merge(offpeak, on='sourcecpNodeId', how='outer')

# also pull markTypeId=1 (actual auction results) where available, for validation
auction = db.getDfFromAwDb(f'''
SELECT sourcecpNodeId, priceMWH as price_onpeak_auctionResult
FROM AW.dbo.ftrOptionPriceMark
WHERE isomarketid=6 AND sinkcpNodeId={SINK} AND ftrBidMarketId={FTR_BID_MARKET}
  AND priceDate='{PRICE_DATE}' AND markTypeId=1 AND priceClassId=2
''')
merged = merged.merge(auction, on='sourcecpNodeId', how='left')

# 2. cpnode names
ids = tuple(int(x) for x in merged.sourcecpNodeId.unique())
names = db.getDfFromAwDb(f'''
SELECT cpnodeid as sourcecpNodeId, name as source_name
FROM AW.dbo.cpNode WHERE cpnodeid IN {ids}
''')
merged = merged.merge(names, on='sourcecpNodeId', how='left')

# 3. bus mapping (latest snapshot per cpNodeID)
busmap = db.getDfFromAwDb(f'''
SELECT cpNodeID as sourcecpNodeId, BusNum, BusName, UPDATE_TIME
FROM AW.dbo.isoErcotCpnodeBus WHERE cpNodeID IN {ids}
''')
busmap = busmap.sort_values('UPDATE_TIME').groupby('sourcecpNodeId').tail(1)[['sourcecpNodeId', 'BusNum', 'BusName']]
merged = merged.merge(busmap, on='sourcecpNodeId', how='left')

# Brandon's own bus
brandon_bus = db.getDfFromAwDb(f'''
SELECT TOP 1 BusNum, BusName FROM AW.dbo.isoErcotCpnodeBus WHERE cpNodeID={SINK} ORDER BY UPDATE_TIME DESC
''')
print('Brandon bus:', brandon_bus.to_dict('records'))
brandon_busnum = int(brandon_bus.BusNum.iloc[0])

# 4. lat/lng via ptoBus -> branchBusLatLng, use most recent ptoBus snapshot with isomarketid corresponding to ERCOT busNums we have
busnums = tuple(int(x) for x in merged.BusNum.dropna().unique().tolist() + [brandon_busnum])
ptobus = db.getDfFromAwDb(f'''
SELECT busNum, branchBusID FROM AW.dbo.ptoBus WHERE busNum IN {busnums}
''')
ptobus = ptobus.drop_duplicates('busNum')
branchids = tuple(int(x) for x in ptobus.branchBusID.dropna().unique())
latlng = db.getDfFromAwDb(f'''
SELECT branchBusID, latitude, longitude FROM AW.dbo.branchBusLatLng WHERE branchBusID IN {branchids}
''')
bus_ll = ptobus.merge(latlng, on='branchBusID', how='left').drop_duplicates('busNum')

merged = merged.merge(bus_ll.rename(columns={'busNum': 'BusNum'}), on='BusNum', how='left')

brandon_ll = bus_ll[bus_ll.busNum == brandon_busnum]
print('Brandon lat/lng:', brandon_ll.to_dict('records'))
blat = float(brandon_ll.latitude.iloc[0]) if len(brandon_ll) and pd.notna(brandon_ll.latitude.iloc[0]) else None
blon = float(brandon_ll.longitude.iloc[0]) if len(brandon_ll) and pd.notna(brandon_ll.longitude.iloc[0]) else None
print('blat/blon', blat, blon)

def haversine_km(lat1, lon1, lat2, lon2):
    if any(pd.isna(v) or v is None for v in (lat1, lon1, lat2, lon2)):
        return None
    R = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dlmb/2)**2
    return 2*R*math.asin(math.sqrt(a))

merged['geo_dist_km_proxy'] = merged.apply(
    lambda r: haversine_km(r.get('latitude'), r.get('longitude'), blat, blon), axis=1
)

out = merged.sort_values('price_onpeak').reset_index(drop=True)
out = out[['sourcecpNodeId', 'source_name', 'BusNum', 'BusName', 'price_onpeak', 'price_offpeak',
           'price_onpeak_auctionResult', 'geo_dist_km_proxy']]
out.to_csv('/workspaces/scratch-workspace/powerflow_analytics/output/brandon_rn_source_candidates.csv', index=False)
print(out.head(30).to_string())
print('total rows', len(out))
