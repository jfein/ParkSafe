import json
import math
from soclient import SoClient
from geocache import GeoCache


meters_per_degree = 111185.10693302986

prefetch_buffer = 1.25


class SocrataLookup:

    crime_cache = GeoCache()
    sign_cache = GeoCache()

    @classmethod
    def get_signs(cls, lat, lon, meters, filter_time=None):
        lat = float(lat)
        lon = float(lon)
        meters = float(meters)
        
        # use cache
        cached_res = cls.sign_cache.get_query(lat, lon, meters)
        if cached_res:
            return cached_res
        
        # Increase meters to pre-load cache
        meters_new = meters * prefetch_buffer
    
        cl = SoClient("data.seattle.gov", "it8u-sznv")
        
        degrees = meters_new / meters_per_degree
        lat_min = lat - degrees
        lat_max = lat + degrees
        lon_min = lon - degrees
        lon_max = lon + degrees
        
        # Filter signs by time
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
            cls.sign_cache.cache_data(d['objectid'], d)
        cls.sign_cache.cache_query(lat, lon, meters_new, [ d['objectid'] for d in data ])

        # return the cached data
        return cls.get_signs(lat, lon, meters)
        
    @classmethod
    def get_sign(cls, id):
        # use cache
        cached_res = cls.sign_cache.get_data(id)
        if cached_res:
            return cached_res
            
        # query
        cl = SoClient("data.seattle.gov", "it8u-sznv")
        data = cl.query(cl.EQUALS(cl.COL("objectid"), cl.VAL(id)))
        if not data:
            return None
            
        # save to cache
        cls.sign_cache.cache_data(data[0]['objectid'], data[0])
        
        return data[0]

    @classmethod
    def get_crimes(cls, lat, lon, meters):
        lat = float(lat)
        lon = float(lon)
        meters = float(meters)
        
        # use cache
        cached_res = cls.crime_cache.get_query(lat, lon, meters)
        if cached_res:
            return cached_res
        
        # Increase meters to pre-load cache
        meters_new = meters * prefetch_buffer
    
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
            cls.crime_cache.cache_data(d['rms_cdw_id'], d)
        cls.crime_cache.cache_query(lat, lon, meters_new, [ d['rms_cdw_id'] for d in data ])
         
        # return the cached data
        return cls.get_crimes(lat, lon, meters)
                
    @classmethod
    def get_crime(cls, id):
        # use cache
        cached_res = cls.crime_cache.get_data(id)
        if cached_res:
            return cached_res
            
        # query and save to cache
        cl = SoClient("data.seattle.gov", "7ais-f98f")
        data = cl.query(cl.EQUALS(cl.COL("rms_cdw_id"), cl.VAL(id)))
        if not data:
            return None    

        # save to cache
        cls.crime_cache.cache_data(data[0]['rms_cdw_id'], data[0])
        
        return data[0]
