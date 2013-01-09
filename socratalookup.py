import json
import math
import tornado.gen
from PySocrataClient.socrataclient import SocrataClient
from geocache import GeoCache


meters_per_degree = 111185.10693302986

prefetch_buffer = 1.25


class SocrataLookup:


    crime_cache = GeoCache()
    sign_cache = GeoCache()
    
    sign_client = SocrataClient("data.seattle.gov", "it8u-sznv")
    crime_client = SocrataClient("data.seattle.gov", "7ais-f98f")

    
    @classmethod
    @tornado.gen.engine
    def get_signs(
            cls, 
            lat, 
            lon, 
            meters, 
            callback=lambda x : x
    ):
        # format input
        lat = float(lat)
        lon = float(lon)
        meters = float(meters)
        
        # Increase meters to pre-load cache
        meters_new = meters * prefetch_buffer

        # load cache
        data = cls.sign_cache.get_query(lat, lon, meters)
        
        # cache is bad, make new request
        if not data:
            # Make a box
            degrees = meters_new / meters_per_degree
            lat_min = lat - degrees
            lat_max = lat + degrees
            lon_min = lon - degrees
            lon_max = lon + degrees
            
            # Load socrata client
            cl = cls.sign_client
            
            query = cl.AND(
                cl.GREATER_THAN(cl.COL("latitude"), cl.VAL(lat_min)),
                cl.LESS_THAN(cl.COL("latitude"), cl.VAL(lat_max)),
                cl.GREATER_THAN(cl.COL("longitude"), cl.VAL(lon_min)),
                cl.LESS_THAN(cl.COL("longitude"), cl.VAL(lon_max)),
                cl.OR(
                    cl.CONTAINS(cl.COL("customtext"), cl.VAL("PARK")), 
                    cl.CONTAINS(cl.COL("categoryde"), cl.VAL("PARK"))
                )
            )
            
            # perform the asynch request
            data = yield tornado.gen.Task(cl.query_rows, query)
            
            # Save to cache
            for d in data:
                cls.sign_cache.cache_data(d['objectid'], d)
            cls.sign_cache.cache_query(lat, lon, meters_new, [ d['objectid'] for d in data ])
        
        callback(data)

        
    @classmethod
    @tornado.gen.engine
    def get_sign(cls, id, callback=lambda x : x):
        # use cache
        data = cls.sign_cache.get_data(id)
        
        # cache is bad, make new request
        if not data:            
            cl = cls.sign_client
            query = cl.EQUALS(cl.COL("objectid"), cl.VAL(id))
            data = yield tornado.gen.Task(cl.query_rows, query)
            
            # extract sign if we got a list back, otherwise will be single item or None
            if type(data) == list:
                if len(data) == 1:
                    data = data[0]
                else:
                    data = None
                
            if data:
                cls.sign_cache.cache_data(data['objectid'], data)
        
        callback(data)

        
    @classmethod
    @tornado.gen.engine
    def get_crimes(
            cls, 
            lat, 
            lon, 
            meters, 
            callback=lambda x : x
    ):
        # format input
        lat = float(lat)
        lon = float(lon)
        meters = float(meters)
        
        # Increase meters to pre-load cache
        meters_new = meters * prefetch_buffer

        # load cache
        data = cls.crime_cache.get_query(lat, lon, meters)
        
        # cache is bad, make new request
        if not data:
            # Make a socrata client            
            cl = cls.crime_client
            
            query = cl.AND(
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
                cl.WITHIN_CIRCLE(cl.COL("location"), cl.VAL(lat), cl.VAL(lon), cl.VAL(meters_new)),
                cl.GREATER_THAN(cl.COL("occurred_date_or_date_range_start"), cl.VAL("1900-01-01T00:00:00"))
            )
            
            # perform the asynch request
            data = yield tornado.gen.Task(cl.query_rows, query)
            
            # Save to cache
            for d in data:
                cls.crime_cache.cache_data(d['rms_cdw_id'], d)
            cls.crime_cache.cache_query(lat, lon, meters_new, [ d['rms_cdw_id'] for d in data ])
            
        callback(data)
         
         
    @classmethod
    @tornado.gen.engine
    def get_crime(cls, id, callback=lambda x : x):
        # use cache
        data = cls.crime_cache.get_data(id)
        
        # cache is bad, make new request
        if not data:            
            cl = cls.crime_client
            query = cl.EQUALS(cl.COL("rms_cdw_id"), cl.VAL(id))
            data = yield tornado.gen.Task(cl.query_rows, query)
            
            # extract sign if we got a list back, otherwise will be single item or None
            if type(data) == list:
                if len(data) == 1:
                    data = data[0]
                else:
                    data = None
                
            if data:
                cls.crime_cache.cache_data(data['rms_cdw_id'], data)
        
        callback(data)