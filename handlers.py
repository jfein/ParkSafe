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
		
		
class HomeHandler(BaseHandler):
	def get(self):
		self.render("index.html")
		
		
class CrimesHandler(BaseHandler):
    def get(self):
		lat = self.get_argument("lat", 0)
		lon = self.get_argument("lon", 0)
		meters = self.get_argument("meters", 10)
		
		res = SocrataLookup.get_crimes(lat, lon, meters)
		
		self.set_header("Content-Type", "application/json")
		self.write(json.dumps(res))
		
		
class SignsHandler(BaseHandler):
    def get(self):
		lat = self.get_argument("lat", 0)
		lon = self.get_argument("lon", 0)
		meters = self.get_argument("meters", 10)
		
		res = SocrataLookup.get_signs(lat, lon, meters)
	
		self.set_header("Content-Type", "application/json")
		self.write(json.dumps(res))