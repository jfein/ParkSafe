import time, math

class CrimeMeta(dict):
    def __init__(self, soc_crime, base_uri):
        self.update(
                id=soc_crime['rms_cdw_id'], 
                latitude=soc_crime['latitude'], 
                longitude=soc_crime['longitude'], 
                description=soc_crime['summarized_offense_description'],  
                date=soc_crime['occurred_date_or_date_range_start'], 
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
        
    def crimeScore(self):
        crimeScore = 0;
        meters_per_degree = 111185.10693302986
        for crime in self.get('crimes'):
            crimeTime = (time.time() - time.mktime(time.strptime(crime['date'], "%Y-%m-%dT%H:%M:%S")))/360000
            crimeTime = 1 if crimeTime <= 0 else crimeTime
            crimeDist = math.sqrt((float(self.get('latitude'))-float(crime['latitude']))**2+(float(self.get('longitude'))-float(crime['longitude']))**2)*meters_per_degree
            crimeScore = crimeScore + math.exp(-1*crimeTime)*math.exp(-1*crimeDist)
            #if (crimeScore <= 0):
        #print crimeScore
        crimeScoreLog= math.log10(crimeScore)
        #print "  " + str(crimeScoreLog)
        return crimeScoreLog + 100
            
        
class Crime(dict):
    def __init__(self, soc_crime, base_uri):
        self.update(
                id=soc_crime['rms_cdw_id'], 
                latitude=soc_crime['latitude'], 
                longitude=soc_crime['longitude'], 
                description=soc_crime['summarized_offense_description'],
                type=soc_crime['offense_type'],
                date=soc_crime['occurred_date_or_date_range_start'],
                block=soc_crime['hundred_block_location'],
                uri=base_uri+"/crimes/"+soc_crime['rms_cdw_id']+".json",
        )