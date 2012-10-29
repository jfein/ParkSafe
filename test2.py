import json
from socratalookup import SocrataLookup

	
lat = 47.7338
lon = -122.329
meters = 50.0

print json.dumps(SocrataLookup.get_signs(lat, lon, meters))