
class CrimeMeta(dict):
    def __init__(self, soc_crime, base_uri):
        self.update(
                id=soc_crime['rms_cdw_id'], 
                latitude=soc_crime['latitude'], 
                longitude=soc_crime['longitude'], 
                description=soc_crime['summarized_offense_description'],  
                uri=base_uri+"/crimes/"+soc_crime['rms_cdw_id']+".json"
        )
        
class SignMeta(dict):
    def __init__(self, soc_sign, base_uri):
        self.update(
                id=soc_sign['objectid'], 
                latitude=soc_sign['latitude'], 
                longitude=soc_sign['longitude'], 
                description=soc_sign['categoryde'],  
                uri=base_uri+"/signs/"+soc_sign['objectid']+".json"
        )
        
class Sign(dict):
    def __init__(self, soc_sign, base_uri):
        self.update(
                id=soc_sign['objectid'], 
                latitude=soc_sign['latitude'], 
                longitude=soc_sign['longitude'], 
                description=soc_sign['categoryde'],
                text=soc_sign['customtext'],
                loc_info=soc_sign['unitdesc'],
                start_time=soc_sign['starttime'],
                end_time=soc_sign['endtime'],
                crimes=soc_sign['crimes'],
                uri=base_uri+"/signs/"+soc_sign['objectid']+".json"
        )
        
class Crime(dict):
    def __init__(self, soc_crime, base_uri):
        self.update(
                id=soc_crime['rms_cdw_id'], 
                latitude=soc_crime['latitude'], 
                longitude=soc_crime['longitude'], 
                description=soc_crime['summarized_offense_description'],
                type=soc_crimep['offense_type'],
                date=soc_crime['occurred_date_or_date_range_start'],
                block=soc_crime['hundred_block_location'],
                uri=base_uri+"/crimes/"+soc_crime['rms_cdw_id']+".json",
        )