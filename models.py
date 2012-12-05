import time, math

def log(x):
    if x <= 0:
        return float("-INF")
    return math.log(x)


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
        self.crimeScore()
        self.crimeCount()  
        
    def crimeScore(self):
        crimeScore = 0;
        meters_per_degree = 111185.10693302986
        for crime in self.get('crimes'):
            crimeTime = (time.time() - time.mktime(time.strptime(crime['date'], "%Y-%m-%dT%H:%M:%S")))/360000
            crimeTime = 1 if crimeTime <= 0 else crimeTime
            crimeDist = math.sqrt((float(self.get('latitude'))-float(crime['latitude']))**2+(float(self.get('longitude'))-float(crime['longitude']))**2)*meters_per_degree
            crimeScore = crimeScore + math.exp(-1*crimeTime)*math.exp(-0.3*crimeDist)
        crimeScoreLog= log(crimeScore)
        self['crime_score'] = -1*crimeScoreLog

    def crimeCount(self):
        seconds_per_month = 2592000
        time_stats = {}
        time_stats['one_month'] = 0
        time_stats['six_months'] = 0
        time_stats['one_year'] = 0;
        time_stats['greater_one_year'] = 0

        for crime in self.get('crimes'):
            crimeTime = time.time() - time.mktime(time.strptime(crime['date'], "%Y-%m-%dT%H:%M:%S"))
            crimeTime = 0 if crimeTime < 0 else crimeTime
            if crimeTime > (seconds_per_month*12):
                time_stats['greater_one_year'] += 1
            elif crimeTime > (seconds_per_month*6):
                time_stats['one_year'] += 1
            elif crimeTime > seconds_per_month:
                time_stats['six_months'] += 1
            else:
                time_stats['one_month'] += 1
        self['crime_time_stats'] = time_stats
        
        
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