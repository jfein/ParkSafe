from socratalookup import SocrataLookup
import tornado.web
import json, datetime
import models

from rdflib import ConjunctiveGraph, URIRef, Literal, Namespace, RDF

GEO = Namespace('http://www.w3.org/2003/01/geo/wgs84_pos#')
DCTERMS = Namespace('http://purl.org/dc/terms/')
DBPEDIAOWL = Namespace('http://dbpedia.org/ontology/')
DBPEDIAPROP = Namespace('http://dbpedia.org/property/')
YAGO = Namespace('http://dbpedia.org/class/yago/')
PARKSAFESIGN = Namespace('http://parksafe.com/terms/signs/')
PARKSAFECRIME = Namespace('http://parksafe.com/terms/crimes/')


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
    def get(self, format):
        lat = self.get_argument("lat", 0)
        lon = self.get_argument("lon", 0)
        meters = self.get_argument("meters", 10)
        
        crimes = SocrataLookup.get_crimes(lat, lon, meters)
        crimes = [ models.CrimeMeta(crime, self.base_uri) for crime in crimes ]
        
        if format is None:
            accept = self.request.headers.get('Accept').lower()
            if "application/rdf+xml" in accept:
                self.set_status(303)
                self.set_header("Location", self.base_uri + "/crimes.rdf?lat=" + lat + "&lon=" + lon + "&meters=" + meters)
            else:
                self.set_status(303)
                self.set_header("Location", self.base_uri + "/crimes.json?lat=" + lat + "&lon=" + lon + "&meters=" + meters)   
        elif format == ".json":
            self.set_header("Content-Type", "application/json")
            self.write(json.dumps(crimes))
        else:
            self.write_error(401, message="Format %s not supported" % format)
        
        
class CrimeHandler(BaseHandler):
    def get(self, id, format):        
        crime = SocrataLookup.get_crime(id)
        crime = models.Crime(crime, self.base_uri)

        # Redirect
        if format is None:
            accept = self.request.headers.get('Accept').lower()
            if "application/rdf+xml" in accept:
                self.set_status(303)
                self.set_header("Location", self.base_uri + "/crimes/" + id + ".rdf")
            else:
                self.set_status(303)
                self.set_header("Location", self.base_uri + "/crimes/" + id + ".json") 
        # JSON
        elif format == ".json":
            self.set_header("Content-Type", "application/json")
            self.write(json.dumps(crime))
        # RDF
        elif format == ".rdf" or format == ".nt" or format == ".ttl":
            graph = ConjunctiveGraph()
            graph.bind('geo', GEO)
            graph.bind('dcterms', DCTERMS)
            graph.bind('dbpediaowl', DBPEDIAOWL)
            graph.bind('parksafecrime', PARKSAFECRIME)
            
            crimeURIRef = URIRef(crime['uri'])
            
            graph.add((crimeURIRef, RDF.type, DBPEDIAOWL['event']))
            graph.add((crimeURIRef, GEO['lat'], Literal(crime['latitude'])))
            graph.add((crimeURIRef, GEO['lon'], Literal(crime['longitude'])))
            graph.add((crimeURIRef, PARKSAFECRIME['description'], Literal(crime['description'])))
            graph.add((crimeURIRef, PARKSAFECRIME['date'], Literal(crime['date'])))
            graph.add((crimeURIRef, PARKSAFECRIME['block'], Literal(crime['block'])))
            graph.add((crimeURIRef, PARKSAFECRIME['type'], Literal(crime['type'])))
            
            if format == ".rdf":
                self.set_header("Content-Type", "application/rdf+xml")
                self.write(graph.serialize())
            elif format == ".nt":
                self.set_header("Content-Type", "text/plain")
                self.write(graph.serialize(format='nt'))
            else:
                self.set_header("Content-Type", "text/turtle")
                self.write(graph.serialize(format='turtle')) 
        else:
            self.write_error(401, message="Format %s not supported" % format)
        
        
class SignsHandler(BaseHandler):
    def get(self, format):
        lat = self.get_argument("lat", 0)
        lon = self.get_argument("lon", 0)
        meters = self.get_argument("meters", 10)
        filter_time = self.get_argument("filter_time", None)
        if filter_time:
            filter_time = datetime.datetime.now().strftime('%H%M')
        
        signs = SocrataLookup.get_signs(lat, lon, meters, filter_time)
        signs = [ models.SignMeta(sign, self.base_uri) for sign in signs ]
    
        if format is None:
            accept = self.request.headers.get('Accept').lower()
            if "application/rdf+xml" in accept:
                self.set_status(303)
                self.set_header("Location", self.base_uri + "/signs.rdf?lat=" + lat + "&lon=" + lon + "&meters=" + meters)
            else:
                self.set_status(303)
                self.set_header("Location", self.base_uri + "/signs.json?lat=" + lat + "&lon=" + lon + "&meters=" + meters)
        elif format == ".json":
            self.set_header("Content-Type", "application/json")
            self.write(json.dumps(signs))
        else:
            self.write_error(401, message="Format %s not supported" % format)

        
class SignHandler(BaseHandler):
    def get(self, id, format):        
        meters = self.get_argument("meters", 250)
    
        sign = SocrataLookup.get_sign(id)
        crimes = SocrataLookup.get_crimes(sign['latitude'], sign['longitude'], meters)
        sign['crimes'] = [ models.CrimeMeta(crime, self.base_uri) for crime in crimes ]
        sign = models.Sign(sign, self.base_uri)

        # Redirect
        if format is None:
            accept = self.request.headers.get('Accept').lower()
            if "application/rdf+xml" in accept:
                self.set_status(303)
                self.set_header("Location", self.base_uri + "/signs/" + id + ".rdf")
            else:
                self.set_status(303)
                self.set_header("Location", self.base_uri + "/signs/" + id + ".json")
        # JSON
        elif format == ".json":
            self.set_header("Content-Type", "application/json")
            self.write(json.dumps(sign))
        # RDF
        elif format == ".rdf" or format == ".nt" or format == ".ttl":
            graph = ConjunctiveGraph()
            graph.bind('geo', GEO)
            graph.bind('dcterms', DCTERMS)
            graph.bind('yago', YAGO)
            graph.bind('parksafesign', PARKSAFESIGN)
            
            signURIRef = URIRef(sign['uri'])
            
            graph.add((signURIRef, RDF.type, YAGO['TrafficSigns']))
            graph.add((signURIRef, GEO['lat'], Literal(sign['latitude'])))
            graph.add((signURIRef, GEO['lon'], Literal(sign['longitude'])))
            graph.add((signURIRef, PARKSAFESIGN['description'], Literal(sign['description'])))
            graph.add((signURIRef, PARKSAFESIGN['text'], Literal(sign['text'])))
            graph.add((signURIRef, PARKSAFESIGN['loc_info'], Literal(sign['loc_info'])))
            graph.add((signURIRef, PARKSAFESIGN['start_time'], Literal(sign['start_time'])))
            graph.add((signURIRef, PARKSAFESIGN['end_time'], Literal(sign['end_time'])))
            graph.add((signURIRef, PARKSAFESIGN['crime_score'], Literal(sign['crime_score'])))
            graph.add((signURIRef, PARKSAFESIGN['crimes_in_month'], Literal(sign['crime_time_stats']['one_month'])))
            graph.add((signURIRef, PARKSAFESIGN['crimes_in_six_months'], Literal(sign['crime_time_stats']['six_months'])))
            graph.add((signURIRef, PARKSAFESIGN['crimes_in_year'], Literal(sign['crime_time_stats']['one_year'])))
            graph.add((signURIRef, PARKSAFESIGN['crimes_greater_one_year'], Literal(sign['crime_time_stats']['greater_one_year'])))


            for crime in sign['crimes']:
                graph.add((signURIRef, PARKSAFESIGN['near'], URIRef(crime['uri'])))
            
            if format == ".rdf":
                self.set_header("Content-Type", "application/rdf+xml")
                self.write(graph.serialize())
            elif format == ".nt":
                self.set_header("Content-Type", "text/plain")
                self.write(graph.serialize(format='nt'))
            else:
                self.set_header("Content-Type", "text/turtle")
                self.write(graph.serialize(format='turtle')) 
        # Unsupported format
        else:
            self.write_error(401, message="Format %s not supported" % format)
            

class QueryHandler(BaseHandler):
    def get(self):
        self.render("query.html")
        
        
class IndexHandler(BaseHandler):
    def get(self):
        self.render("index.html")