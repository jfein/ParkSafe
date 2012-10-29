import json
from socratalookup import SocrataLookup


res = SocrataLookup.get_crimes(47.5925, -122.3252, 250)
	
print json.dumps(res[:3])