import json
from soclient import SoClient

cl = SoClient("data.seattle.gov", "7ais-f98f")

res = cl.query(
    cl.AND(
        cl.EQUALS(cl.COL("offense_type"), cl.VAL("VEH-THEFT-AUTO")), 
        cl.CIRCLE("location", 47.5925, -122.3252, 2500)
    )
)


print json.dumps(res)