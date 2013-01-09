import json
import datetime
import models
import tornado.web
import tornado.gen
from rdflib import ConjunctiveGraph, URIRef, Literal, Namespace, RDF
from socratalookup import SocrataLookup


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
        self.write("Error {status_code} - {message}".format(**locals()))
        
        
class CrimesHandler(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self, format):
        # GET arguments
        lat = self.get_argument("lat", 0)
        lon = self.get_argument("lon", 0)
        meters = self.get_argument("meters", 10)
    
        # Content negotiation
        if format is None:
            accept = self.request.headers.get('Accept').lower()
            if "application/rdf+xml" in accept:
                self.set_status(303)
                self.set_header("Location", self.base_uri + "/crimes.rdf?lat=" + lat + "&lon=" + lon + "&meters=" + meters)
            else:
                self.set_status(303)
                self.set_header("Location", self.base_uri + "/crimes.json?lat=" + lat + "&lon=" + lon + "&meters=" + meters)
            self.finish()
        # Format not supported
        if format != ".json":
            self.write_error(401, message="Format %s not supported" % format)
            self.finish()
        # Get data and serve the JSON request
        else:
            crimes = yield tornado.gen.Task(SocrataLookup.get_crimes, lat, lon, meters)
            
            # Connection still good, send data
            if not self.request.connection.stream.closed():
                crimes = [ models.CrimeMeta(crime, self.base_uri) for crime in crimes ]

                self.set_header("Content-Type", "application/json")
                self.finish(json.dumps(crimes))                     
        
        
class CrimeHandler(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self, id, format):        
        # Content negotiation
        if format is None:
            accept = self.request.headers.get('Accept').lower()
            if "application/rdf+xml" in accept:
                self.set_status(303)
                self.set_header("Location", self.base_uri + "/signs/" + id + ".rdf")
            else:
                self.set_status(303)
                self.set_header("Location", self.base_uri + "/signs/" + id + ".json")
            self.finish()
        # invalid format
        elif format != ".json" and format != ".rdf":
            self.write_error(401, message="Format %s not supported" % format)
            self.finish()
        # call socrata
        else:
            crime = yield tornado.gen.Task(SocrataLookup.get_crime, id)
            # Connection still good after calling socrata
            if not self.request.connection.stream.closed():
                if not crime:
                    self.write_error(404, message="crime not found")
                    self.finish()         
                else:
                    crime = models.Crime(crime, self.base_uri)
                
                    # JSON
                    if format == ".json":
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
                    self.finish()
        
        
class SignsHandler(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self, format):
        # GET arguments
        lat = self.get_argument("lat", 0)
        lon = self.get_argument("lon", 0)
        meters = self.get_argument("meters", 10)

        # Content negotiation
        if format is None:
            accept = self.request.headers.get('Accept').lower()
            if "application/rdf+xml" in accept:
                self.set_status(303)
                self.set_header("Location", self.base_uri + "/signs.rdf?lat=" + lat + "&lon=" + lon + "&meters=" + meters)
            else:
                self.set_status(303)
                self.set_header("Location", self.base_uri + "/signs.json?lat=" + lat + "&lon=" + lon + "&meters=" + meters)
            self.finish()
        # Format not supported
        if format != ".json":
            self.write_error(401, message="Format %s not supported" % format)
            self.finish()
        # Get data and serve the JSON request
        else:
            signs = yield tornado.gen.Task(SocrataLookup.get_signs, lat, lon, meters)

            # Connection still good, send data
            if not self.request.connection.stream.closed():
                signs = [ models.SignMeta(sign, self.base_uri) for sign in signs ]

                self.set_header("Content-Type", "application/json")
                self.finish(json.dumps(signs))


class SignHandler(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self, id, format):        
        meters = self.get_argument("meters", 250)

        # Content negotiation
        if format is None:
            accept = self.request.headers.get('Accept').lower()
            if "application/rdf+xml" in accept:
                self.set_status(303)
                self.set_header("Location", self.base_uri + "/signs/" + id + ".rdf")
            else:
                self.set_status(303)
                self.set_header("Location", self.base_uri + "/signs/" + id + ".json")
            self.finish()
        # invalid format
        elif format != ".json" and format != ".rdf":
            self.write_error(401, message="Format %s not supported" % format)
            self.finish()
        # call socrata
        else:
            sign = yield tornado.gen.Task(SocrataLookup.get_sign, id)
            # Connection still good after calling socrata
            if not self.request.connection.stream.closed():
                if not sign:
                    self.write_error(404, message="sign not found")
                    self.finish()         
                else:
                    crimes = yield tornado.gen.Task(SocrataLookup.get_crimes, sign['latitude'], sign['longitude'], meters)
                    # Connection still good after calling socrata
                    if not self.request.connection.stream.closed():
                        # format sign and crimes
                        if crimes:
                            sign['crimes'] = [ models.CrimeMeta(crime, self.base_uri) for crime in crimes ]
                        else:
                            sign['crimes'] = []
                        sign = models.Sign(sign, self.base_uri)
                    
                        # JSON
                        if format == ".json":
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
                    
                        self.finish()
            

class QueryHandler(BaseHandler):
    def get(self):
        self.render("query.html")
        
        
class IndexHandler(BaseHandler):
    def get(self):
        self.render("index.html")