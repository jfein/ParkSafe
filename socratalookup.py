import json
import math
from soclient import SoClient


meters_per_degree = 111185.10693302986

prefetch_buffer = 300


class SocrataLookup:

    crimes_queries = {}
    signs_queries = {}
    
    crimes = {}
    signs = {}

    @classmethod
    def get_signs(cls, lat, lon, meters, filter_time=None):
        lat = float(lat)
        lon = float(lon)
        meters = float(meters)
        
        # check if we can use cache
        for (lat_q, lon_q, meters_q) in cls.signs_queries:
            delta_lat = (lat_q - lat) * meters_per_degree
            delta_lon = (lon_q - lon) * meters_per_degree
            distance_btwn_centers = math.sqrt(delta_lat*delta_lat + delta_lon*delta_lon)     

            # we have performed this query before
            if (distance_btwn_centers + meters) <= meters_q:
                degrees = meters / meters_per_degree
                lat_min = lat - degrees
                lat_max = lat + degrees
                lon_min = lon - degrees
                lon_max = lon + degrees
                signs = []
                for sign_id in cls.signs_queries[(lat_q, lon_q, meters_q)]:
                    sign = cls.signs[sign_id]
                    sign_lat = float(sign['latitude'])
                    sign_lon = float(sign['longitude'])
                    # crime from old query also matches this query
                    if sign_lat >= lat_min and sign_lat <= lat_max and sign_lon >= lon_min and sign_lon <= lon_max:
                        signs.append(sign)
                return signs
        
        # Increase meters to pre-load cache
        meters_new = meters + prefetch_buffer
    
        cl = SoClient("data.seattle.gov", "it8u-sznv")
        
        degrees = meters_new / meters_per_degree

        lat_min = lat - degrees
        lat_max = lat + degrees

        lon_min = lon - degrees
        lon_max = lon + degrees
        
        if filter_time:
            term = cl.AND(
                cl.GREATER_THAN_OR_EQUALS(cl.COL("starttime"), cl.VAL(filter_time)),
                cl.LESS_THAN_OR_EQUALS(cl.COL("endtime"), cl.VAL(filter_time)), 
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
        cls.signs_queries[(lat, lon, meters_new)] = [ d['objectid'] for d in data ]

        # return the cached data
        return cls.get_signs(lat, lon, meters)
        
        
    @classmethod
    def get_sign(cls, id):
        # use cache
        if id in cls.signs:
            return cls.signs[id]
            
        # query and save to cache
        cl = SoClient("data.seattle.gov", "it8u-sznv")
        data = cl.query(cl.EQUALS(cl.COL("objectid"), cl.VAL(id)))
        if not data:
            return None
            
        # save to cache
        cls.signs[data[0]['objectid']] = data[0]
        
        return data[0]

    @classmethod
    def get_crimes(cls, lat, lon, meters):
        lat = float(lat)
        lon = float(lon)
        meters = float(meters)
        
        # check if we can use cache
        for (lat_q, lon_q, meters_q) in cls.crimes_queries:
            delta_lat = (lat_q - lat) * meters_per_degree
            delta_lon = (lon_q - lon) * meters_per_degree
            distance_btwn_centers = math.sqrt(delta_lat*delta_lat + delta_lon*delta_lon)            
            # we have performed this query before
            if (distance_btwn_centers + meters) <= meters_q:
                degrees = meters / meters_per_degree
                lat_min = lat - degrees
                lat_max = lat + degrees
                lon_min = lon - degrees
                lon_max = lon + degrees
                crimes = []
                for crime_id in cls.crimes_queries[(lat_q, lon_q, meters_q)]:
                    crime = cls.crimes[crime_id]
                    crime_lat = float(crime['latitude'])
                    crime_lon = float(crime['longitude'])
                    # crime from old query also matches this query
                    if crime_lat >= lat_min and crime_lat <= lat_max and crime_lon >= lon_min and crime_lon <= lon_max:
                        crimes.append(crime)
                return crimes
        
        # Increase meters to pre-load cache
        meters_new = meters + prefetch_buffer
    
        cl = SoClient("data.seattle.gov", "7ais-f98f")

        data = cl.query(
            cl.AND(
                cl.OR(
                    cl.EQUALS(cl.COL("offense_type"), cl.VAL("THEFT-CARPROWL")),
                    cl.EQUALS(cl.COL("offense_type"), cl.VAL("VEH-THEFT-AUTO")),
                    cl.EQUALS(cl.COL("offense_type"), cl.VAL("BURGLARY-FORCE-RES")),
                    cl.EQUALS(cl.COL("offense_type"), cl.VAL("ASSLT-NONAGG")),
                    cl.EQUALS(cl.COL("offense_type"), cl.VAL("WARRARR-FELONY")),
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
                cl.CIRCLE("location", lat, lon, meters_new),
                cl.GREATER_THAN(cl.COL("occurred_date_or_date_range_start"), cl.VAL("1900-01-01T00:00:00"))
            )
        )
        
        # Save to cache
        for d in data:
            cls.crimes[d['rms_cdw_id']] = d
        cls.crimes_queries[(lat, lon, meters_new)] = [ d['rms_cdw_id'] for d in data ]
        
        # return the cached data
        return cls.get_crimes(lat, lon, meters)
                
    @classmethod
    def get_crime(cls, id):
        # use cache
        if id in cls.crimes:
            return cls.crimes[id]
            
        # query and save to cache
        cl = SoClient("data.seattle.gov", "7ais-f98f")
        data = cl.query(cl.EQUALS(cl.COL("rms_cdw_id"), cl.VAL(id)))
        if not data:
            return None    

        # save to cache
        cls.crimes[data[0]['rms_cdw_id']] = data[0]
        
        return data[0]
