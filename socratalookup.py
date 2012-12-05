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
    def get_signs(cls, lat, lon, meters, callback):
        # format input
        lat = float(lat)
        lon = float(lon)
        meters = float(meters)
        
        # Increase meters to pre-load cache
        meters_new = meters * prefetch_buffer
        
        # the callback upon this function success
        def query_callback(data):
            # Save to cache
            for d in data:
                cls.sign_cache.cache_data(d['objectid'], d)
            cls.sign_cache.cache_query(lat, lon, meters_new, [ d['objectid'] for d in data ])
            # call the callback w/ the data
            callback(data)
        
        # use cache
        cached_res = cls.sign_cache.get_query(lat, lon, meters)
        if cached_res:
            query_callback(cached_res)
            return
            
        # Make a box
        degrees = meters_new / meters_per_degree
        lat_min = lat - degrees
        lat_max = lat + degrees
        lon_min = lon - degrees
        lon_max = lon + degrees
        
        # Make a socrata client
        cl = SoClient("data.seattle.gov", "it8u-sznv")
        
        # perform the asynch request
        cl.query_a(
            cl.AND(
                cl.GREATER_THAN(cl.COL("latitude"), cl.VAL(lat_min)),
                cl.LESS_THAN(cl.COL("latitude"), cl.VAL(lat_max)),
                cl.GREATER_THAN(cl.COL("longitude"), cl.VAL(lon_min)),
                cl.LESS_THAN(cl.COL("longitude"), cl.VAL(lon_max)),
                cl.OR(
                    cl.CONTAINS(cl.COL("customtext"), cl.VAL("PARK")), 
                    cl.CONTAINS(cl.COL("categoryde"), cl.VAL("PARK"))
                )
            ),
            query_callback
        )

        
    @classmethod
    def get_sign(cls, id, callback):
        # the callback upon this api query success
        def query_callback(data):
            if type(data) != list:
                callback(data)
            elif len(data) != 1:
                callback(None)
            else:
                if 'crimes' in data[0]:
                    print "FUCK"
                cls.sign_cache.cache_data(data[0]['objectid'], data[0])
                callback(data[0])
    
        # use cache
        cached_res = cls.sign_cache.get_data(id)
        if cached_res:
            query_callback(cached_res)
            return
            
        # query
        cl = SoClient("data.seattle.gov", "it8u-sznv")
        cl.query_a(cl.EQUALS(cl.COL("objectid"), cl.VAL(id)), query_callback)

        
    @classmethod
    def get_crimes(cls, lat, lon, meters, callback):
        # format input
        lat = float(lat)
        lon = float(lon)
        meters = float(meters)
        
        # Increase meters to pre-load cache
        meters_new = meters * prefetch_buffer
        
        # the callback upon this function success
        def query_callback(data):
            # Save to cache
            for d in data:
                cls.crime_cache.cache_data(d['rms_cdw_id'], d)
            cls.crime_cache.cache_query(lat, lon, meters_new, [ d['rms_cdw_id'] for d in data ])
            # call the callback w/ the data
            callback(data)
        
        # use cache
        cached_res = cls.crime_cache.get_query(lat, lon, meters)
        if cached_res:
            query_callback(cached_res)
            return

        # Make a socrata client            
        cl = SoClient("data.seattle.gov", "7ais-f98f")

        # perform the asynch request
        cl.query_a(
            cl.AND(
                cl.OR(
                    cl.EQUALS(cl.COL("offense_type"), cl.VAL("THEFT-CARPROWL")),
                    cl.EQUALS(cl.COL("offense_type"), cl.VAL("VEH-THEFT-AUTO")),
                    cl.EQUALS(cl.COL("offense_type"), cl.VAL("BURGLARY-FORCE-RES")),
                    cl.EQUALS(cl.COL("offense_type"), cl.VAL("ASSLT-NONAGG")),
                    cl.EQUALS(cl.COL("offense_type"), cl.VAL("BURGLARY-NOFORCE-RES")),
                    cl.EQUALS(cl.COL("offense_type"), cl.VAL("BURGLARY-FORCE-NONRES")),
                    cl.EQUALS(cl.COL("offense_type"), cl.VAL("THEFT-AUTOACC")),
                    cl.EQUALS(cl.COL("offense_type"), cl.VAL("THEFT-BICYCLE")),
                    cl.EQUALS(cl.COL("offense_type"), cl.VAL("ROBBERY-STREET-BODYFORCE")),
                    cl.EQUALS(cl.COL("offense_type"), cl.VAL("ASSLT-AGG-WEAPON")),
                    cl.EQUALS(cl.COL("offense_type"), cl.VAL("BURGLARY-NOFORCE-NONRES")),
                    cl.EQUALS(cl.COL("offense_type"), cl.VAL("THEFT-LICENSE PLATE")),
                    cl.EQUALS(cl.COL("offense_type"), cl.VAL("VEH-RCVD-FOR OTHER AGENCY")),
                    cl.EQUALS(cl.COL("offense_type"), cl.VAL("BURGLARY-SECURE PARKING-RES")),
                    cl.EQUALS(cl.COL("offense_type"), cl.VAL("ASSLT-AGG-BODYFORCE")),
                    cl.EQUALS(cl.COL("offense_type"), cl.VAL("DUI-LIQUOR")),
                    cl.EQUALS(cl.COL("offense_type"), cl.VAL("VEH-THEFT-TRUCK")),
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
                    cl.EQUALS(cl.COL("offense_type"), cl.VAL("ROBBERY-BUSINESS-GUN")),
                    cl.EQUALS(cl.COL("offense_type"), cl.VAL("ROBBERY-BUSINESS-WEAPON")),
                    cl.EQUALS(cl.COL("offense_type"), cl.VAL("ROBBERY-RESIDENCE-BODYFORCE")),
                    cl.EQUALS(cl.COL("offense_type"), cl.VAL("ROBBERY-RESIDENCE-GUN")),
                    cl.EQUALS(cl.COL("offense_type"), cl.VAL("VEH-THEFT-TRAILER")),
                    cl.EQUALS(cl.COL("offense_type"), cl.VAL("WEAPON-CONCEALED"))
                ),
                cl.CIRCLE("location", lat, lon, meters_new),
                cl.GREATER_THAN(cl.COL("occurred_date_or_date_range_start"), cl.VAL("1900-01-01T00:00:00"))
            ),
            query_callback
        )
         
         
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
