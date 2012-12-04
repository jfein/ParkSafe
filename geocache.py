import math

class GeoCache(dict):

    meters_per_degree = 111185.10693302986

    def __init__(self):
        self['queries'] = {}
        self['data'] = {}
    
    def cache_query(self, lat, lon, r, ids):
        self['queries'][(lat, lon, r)] = ids
        
    def cache_data(self, id, data):
        self['data'][id] = data
        
    def get_data(self, id):
        return self['data'].get(id, None)
        
    def get_query(self, lat, lon, r):
        for (lat_q, lon_q, meters_q), ids in self['queries'].iteritems():
            # If exact query was already made, store results
            if lat_q == lat and lon_q == lon and meters_q == r:
                return [ self['data'][id] for id in ids ]
            delta_lat = (lat_q - lat) * GeoCache.meters_per_degree
            delta_lon = (lon_q - lon) * GeoCache.meters_per_degree
            distance_btwn_centers = math.sqrt(delta_lat*delta_lat + delta_lon*delta_lon)   
            # we have performed this query before
            if (distance_btwn_centers + r) <= meters_q:
                degrees = r / GeoCache.meters_per_degree
                lat_min = lat - degrees
                lat_max = lat + degrees
                lon_min = lon - degrees
                lon_max = lon + degrees
                datas = []
                for id in ids:
                    data = self['data'][id]
                    data_lat = float(data['latitude'])
                    data_lon = float(data['longitude'])
                    # crime from old query also matches this query
                    if data_lat >= lat_min and data_lat <= lat_max and data_lon >= lon_min and data_lon <= lon_max:
                        datas.append(data)
                return datas
        return None
        

if __name__ == "__main__":
    cache = GeoCache()
    
    lat = 42.10
    lon = 110.10
    meters = 100.0
    data = [ dict(id=i, latitude=42.10, longitude=110.10) for i in range(3) ]
    
    for d in data:
        cache.cache_data(d['id'], d)
        
    cache.cache_query(lat, lon, meters, [ d['id'] for d in data ])
    
    print cache.get_query(lat, lon, meters - 10)
        