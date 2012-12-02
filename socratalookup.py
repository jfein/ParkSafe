import json
from soclient import SoClient


class SocrataLookup:

    crimes = {}
    signs = {}

    @classmethod
    def get_signs(cls, base_uri, lat, lon, meters, filter_time=None):
        lat = float(lat)
        lon = float(lon)
        meters = float(meters)
    
        cl = SoClient("data.seattle.gov", "it8u-sznv")
        
        meters_per_degree = 111185.10693302986
        degrees = meters / meters_per_degree

        lat_min = lat - degrees
        lat_max = lat + degrees

        lon_min = lon - degrees
        lon_max = lon + degrees
        
        if filter_time:
            term = cl.AND(
                cl.GREATER_THAN(cl.COL("starttime"), cl.VAL(filter_time)),
                cl.LESS_THAN(cl.COL("endtime"), cl.VAL(filter_time)), 
            )
        else:
            term = cl.AND()
        
        data = cl.query(
            cl.AND(
                cl.GREATER_THAN(cl.COL("latitude"), cl.VAL(lat_min)),
                cl.LESS_THAN(cl.COL("latitude"), cl.VAL(lat_max)),
                cl.GREATER_THAN(cl.COL("longitude"), cl.VAL(lon_min)),
                cl.LESS_THAN(cl.COL("longitude"), cl.VAL(lon_max)),
                cl.OR(
                    cl.CONTAINS(cl.COL("customtext"), cl.VAL("PARK")), 
                    cl.CONTAINS(cl.COL("categoryde"), cl.VAL("PARK"))
                ),
                term
            )
        )
        
        # Save to cache
        for d in data:
            cls.signs[d['objectid']] = d
        
        return [ dict(
                    objectid=d['objectid'], 
                    latitude=d['latitude'], 
                    longitude=d['longitude'], 
                    categoryde=d['categoryde'],  
                    uri=base_uri+"/signs/"+d['objectid']+".json"
                ) for d in data ]
        
    @classmethod
    def get_sign(cls, id):
        # use cache
        if id in cls.signs:
            return cls.signs[id]
            
        # query and save to cache
        cl = SoClient("data.seattle.gov", "it8u-sznv")
        data = cl.query(cl.EQUALS(cl.COL("objectid"), cl.VAL(id)))[0]
        cls.signs[data['objectid']] = data
        return data

    @classmethod
    def get_crimes(cls, base_uri, lat, lon, meters):
        cl = SoClient("data.seattle.gov", "7ais-f98f")

        data = cl.query(
            cl.AND(
                cl.OR(
                    cl.EQUALS(cl.COL("offense_type"), cl.VAL("THEFT-CARPROWL")),
                    cl.EQUALS(cl.COL("offense_type"), cl.VAL("THEFT-OTH")),
                    cl.EQUALS(cl.COL("offense_type"), cl.VAL("VEH-THEFT-AUTO")),
                    cl.EQUALS(cl.COL("offense_type"), cl.VAL("BURGLARY-FORCE-RES")),
                    cl.EQUALS(cl.COL("offense_type"), cl.VAL("ASSLT-NONAGG")),
                    cl.EQUALS(cl.COL("offense_type"), cl.VAL("WARRARR-FELONY")),
                    cl.EQUALS(cl.COL("offense_type"), cl.VAL("DISTURBANCE-OTH")),
                    cl.EQUALS(cl.COL("offense_type"), cl.VAL("BURGLARY-NOFORCE-RES")),
                    cl.EQUALS(cl.COL("offense_type"), cl.VAL("BURGLARY-FORCE-NONRES")),
                    cl.EQUALS(cl.COL("offense_type"), cl.VAL("THEFT-AUTOACC")),
                    cl.EQUALS(cl.COL("offense_type"), cl.VAL("HARASSMENT")),
                    cl.EQUALS(cl.COL("offense_type"), cl.VAL("THEFT-BICYCLE")),
                    cl.EQUALS(cl.COL("offense_type"), cl.VAL("ROBBERY-STREET-BODYFORCE")),
                    cl.EQUALS(cl.COL("offense_type"), cl.VAL("ASSLT-AGG-WEAPON")),
                    cl.EQUALS(cl.COL("offense_type"), cl.VAL("BURGLARY-NOFORCE-NONRES")),
                    cl.EQUALS(cl.COL("offense_type"), cl.VAL("THEFT-LICENSE PLATE")),
                    cl.EQUALS(cl.COL("offense_type"), cl.VAL("VEH-RCVD-FOR OTHER AGENCY")),
                    cl.EQUALS(cl.COL("offense_type"), cl.VAL("BURGLARY-SECURE PARKING-RES")),
                    cl.EQUALS(cl.COL("offense_type"), cl.VAL("NARC-SELL-COCAINE")),
                    cl.EQUALS(cl.COL("offense_type"), cl.VAL("ASSLT-AGG-BODYFORCE")),
                    cl.EQUALS(cl.COL("offense_type"), cl.VAL("DUI-LIQUOR")),
                    cl.EQUALS(cl.COL("offense_type"), cl.VAL("VEH-THEFT-TRUCK")),
                    cl.EQUALS(cl.COL("offense_type"), cl.VAL("PROSTITUTION")),
                    cl.EQUALS(cl.COL("offense_type"), cl.VAL("THEFT-PKPOCKET")),
                    cl.EQUALS(cl.COL("offense_type"), cl.VAL("WEAPON-POSSESSION")),
                    cl.EQUALS(cl.COL("offense_type"), cl.VAL("VEH-THEFT-MTRCYCLE")),
                    cl.EQUALS(cl.COL("offense_type"), cl.VAL("ROBBERY-STREET-WEAPON")),
                    cl.EQUALS(cl.COL("offense_type"), cl.VAL("ROBBERY-STREET-GUN")),
                    cl.EQUALS(cl.COL("offense_type"), cl.VAL("THEFT-AUTO PARTS")),
                    cl.EQUALS(cl.COL("offense_type"), cl.VAL("PROPERTY STOLEN-POSSESS")),
                    cl.EQUALS(cl.COL("offense_type"), cl.VAL("ASSLT-NONAGG-POLICE")),
                    cl.EQUALS(cl.COL("offense_type"), cl.VAL("ASSLT-AGG-GUN")),
                    cl.EQUALS(cl.COL("offense_type"), cl.VAL("VEH-RCVD-FOR OTHAGY")),
                    cl.EQUALS(cl.COL("offense_type"), cl.VAL("BURGLARY-SECURE PARKING-NONRES")),
                    cl.EQUALS(cl.COL("offense_type"), cl.VAL("WEAPON-UNLAWFUL USE")),
                    cl.EQUALS(cl.COL("offense_type"), cl.VAL("THREATS-WEAPON")),
                    cl.EQUALS(cl.COL("offense_type"), cl.VAL("ROBBERY-BUSINESS-GUN")),
                    cl.EQUALS(cl.COL("offense_type"), cl.VAL("ROBBERY-BUSINESS-WEAPON")),
                    cl.EQUALS(cl.COL("offense_type"), cl.VAL("INJURY - OTHER")),
                    cl.EQUALS(cl.COL("offense_type"), cl.VAL("INJURY - ACCIDENTAL")),
                    cl.EQUALS(cl.COL("offense_type"), cl.VAL("NARC-SELL-HEROIN")),
                    cl.EQUALS(cl.COL("offense_type"), cl.VAL("ROBBERY-RESIDENCE-BODYFORCE")),
                    cl.EQUALS(cl.COL("offense_type"), cl.VAL("ROBBERY-RESIDENCE-GUN")),
                    cl.EQUALS(cl.COL("offense_type"), cl.VAL("VEH-THEFT-TRAILER")),
                    cl.EQUALS(cl.COL("offense_type"), cl.VAL("WEAPON-CONCEALED"))
                ),
                cl.CIRCLE("location", lat, lon, meters),
                cl.GREATER_THAN(cl.COL("occurred_date_or_date_range_start"), cl.VAL("1900-01-01T00:00:00"))
            )
        )
        
        # Save to cache
        for d in data:
            cls.crimes[d['rms_cdw_id']] = d
        
        return [ dict(
                    rms_cdw_id=d['rms_cdw_id'], 
                    latitude=d['latitude'], 
                    longitude=d['longitude'], 
                    summarized_offense_description=d['summarized_offense_description'],  
                    uri=base_uri+"/crimes/"+d['rms_cdw_id']+".json"
                ) for d in data ]
                
    @classmethod
    def get_crime(cls, id):
        # use cache
        if id in cls.crimes:
            return cls.crimes[id]
            
        # query and save to cache
        cl = SoClient("data.seattle.gov", "7ais-f98f")
        data = cl.query(cl.EQUALS(cl.COL("rms_cdw_id"), cl.VAL(id)))[0]
        cls.crimes[data['rms_cdw_id']] = data
        return data