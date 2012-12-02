from socratalookup import SocrataLookup

import tornado.web
import json


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
        
        res = SocrataLookup.get_crimes(self.base_uri, lat, lon, meters)
        
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(res))
        
        
class CrimeHandler(BaseHandler):
    def get(self, id):        
        res = SocrataLookup.get_crime(id)
    
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(res))
        
        
class SignsHandler(BaseHandler):
    def get(self):
        lat = self.get_argument("lat", 0)
        lon = self.get_argument("lon", 0)
        meters = self.get_argument("meters", 10)
        
        res = SocrataLookup.get_signs(self.base_uri, lat, lon, meters)
    
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(res))

        
class SignHandler(BaseHandler):
    def get(self, id):        
        distance = self.get_argument("distance", 20)
    
        sign = SocrataLookup.get_sign(id)
        crimes = SocrataLookup.get_crimes(self.base_uri, sign['latitude'], sign['longitude'], distance)
        sign['crimes'] = crimes

    
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(sign))
        

class QueryHandler(BaseHandler):
    def get(self):
        self.render("query.html")
        
        
class IndexHandler(BaseHandler):
    def get(self):
        self.render("index.html")