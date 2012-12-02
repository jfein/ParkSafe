from socratalookup import SocrataLookup
import tornado.web
import json, datetime


class BaseHandler(tornado.web.RequestHandler):       
    @property
    def base_uri(self):
        protocol = self.request.protocol
        host = self.request.headers.get('Host')
        return protocol + "://" + host
        
    def write_error(self, status_code, message):
        self.set_status(status_code)
        self.finish("Error {status_code} - {message}".format(**locals()))
        
        
class CrimesHandler(BaseHandler):
    def get(self):
        lat = self.get_argument("lat", 0)
        lon = self.get_argument("lon", 0)
        meters = self.get_argument("meters", 10)
        
        crimes = SocrataLookup.get_crimes(lat, lon, meters)
        crimes = [ 
            dict(
                rms_cdw_id=crime['rms_cdw_id'], 
                latitude=crime['latitude'], 
                longitude=crime['longitude'], 
                summarized_offense_description=crime['summarized_offense_description'],  
                uri=self.base_uri+"/crimes/"+crime['rms_cdw_id']+".json"
            )
            for crime in crimes 
        ]
        
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(crimes))
        
        
class CrimeHandler(BaseHandler):
    def get(self, id):        
        crime = SocrataLookup.get_crime(id)
    
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(crime))
        
        
class SignsHandler(BaseHandler):
    def get(self):
        lat = self.get_argument("lat", 0)
        lon = self.get_argument("lon", 0)
        meters = self.get_argument("meters", 10)
        filter_time = self.get_argument("filter_time", None)
        
        if filter_time:
            filter_time = datetime.datetime.now().strftime('%H%M')
        
        signs = SocrataLookup.get_signs(lat, lon, meters, filter_time)
        signs = [ 
            dict(
                objectid=sign['objectid'], 
                latitude=sign['latitude'], 
                longitude=sign['longitude'], 
                categoryde=sign['categoryde'],  
                uri=self.base_uri+"/signs/"+sign['objectid']+".json"
            )
            for sign in signs 
        ]
    
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(signs))

        
class SignHandler(BaseHandler):
    def get(self, id):        
        meters = self.get_argument("meters", 100)
    
        sign = SocrataLookup.get_sign(id)
        crimes = SocrataLookup.get_crimes(sign['latitude'], sign['longitude'], meters)
        sign['crimes'] = [ 
            dict(
                rms_cdw_id=crime['rms_cdw_id'], 
                latitude=crime['latitude'], 
                longitude=crime['longitude'], 
                summarized_offense_description=crime['summarized_offense_description'],  
                uri=self.base_uri+"/crimes/"+crime['rms_cdw_id']+".json"
            )
            for crime in crimes 
        ]
    
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(sign))
        

class QueryHandler(BaseHandler):
    def get(self):
        self.render("query.html")
        
        
class IndexHandler(BaseHandler):
    def get(self):
        self.render("index.html")