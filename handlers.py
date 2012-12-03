from socratalookup import SocrataLookup
import tornado.web
import json, datetime

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
        
        filteredCrime = {}
        filteredCrime['rms_cdw_id'] = crime['rms_cdw_id']
        filteredCrime['latitude'] = crime['latitude']
        filteredCrime['longitude'] = crime['longitude']
        filteredCrime['summarized_offense_description'] = crime['summarized_offense_description']
        filteredCrime['occurred_date_or_date_range_start'] = crime['occurred_date_or_date_range_start']
        filteredCrime['hundred_block_location'] = crime['hundred_block_location']
        filteredCrime['offense_type'] = crime['offense_type']
        
        if format is None:
            accept = self.request.headers.get('Accept').lower()
            if "application/rdf+xml" in accept:
                self.set_status(303)
                self.set_header("Location", self.base_uri + "/crimes/" + id + ".rdf")
            else:
                self.set_status(303)
                self.set_header("Location", self.base_uri + "/crimes/" + id + ".json") 
        elif format == ".json":
            self.set_header("Content-Type", "application/json")
            self.write(json.dumps(filteredCrime))
        elif format == ".rdf" or format == ".nt" or format == ".ttl":
            graph = ConjunctiveGraph()
            graph.bind('geo', GEO)
            graph.bind('dcterms', DCTERMS)
            graph.bind('dbpediaowl', DBPEDIAOWL)
            graph.bind('parksafecrime', PARKSAFECRIME)
            
            crimeURI = self.base_uri + "/crimes/" + id
            
            graph.add((URIRef(crimeURI), RDF.type, DBPEDIAOWL['event']))
            graph.add((URIRef(crimeURI), GEO['lat'], Literal(filteredCrime['latitude'])))
            graph.add((URIRef(crimeURI), GEO['lon'], Literal(filteredCrime['longitude'])))
            graph.add((URIRef(crimeURI), PARKSAFECRIME['offenseDescription'], Literal(filteredCrime['summarized_offense_description'])))
            graph.add((URIRef(crimeURI), PARKSAFECRIME['occuredDate'], Literal(filteredCrime['occurred_date_or_date_range_start'])))
            graph.add((URIRef(crimeURI), PARKSAFECRIME['blockInformation'], Literal(filteredCrime['hundred_block_location'])))
            graph.add((URIRef(crimeURI), PARKSAFECRIME['offenseType'], Literal(filteredCrime['offense_type'])))
            
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
        meters = self.get_argument("meters", 100)
    
        sign = SocrataLookup.get_sign(id)
        
        filteredSign = {}
        filteredSign['objectid'] = sign['objectid'] 
        filteredSign['latitude'] = sign['latitude']
        filteredSign['longitude'] = sign['longitude']
        filteredSign['categoryde'] = sign['categoryde']
        filteredSign['customtext'] = sign['customtext']
        filteredSign['unitdesc'] = sign['unitdesc']
        filteredSign['starttime'] = sign['starttime']
        filteredSign['endtime'] = sign['endtime']
        
        crimes = SocrataLookup.get_crimes(sign['latitude'], sign['longitude'], meters)
        filteredSign['crimes'] = [ 
            dict(
                rms_cdw_id=crime['rms_cdw_id'], 
                latitude=crime['latitude'], 
                longitude=crime['longitude'], 
                summarized_offense_description=crime['summarized_offense_description'],  
                uri=self.base_uri+"/crimes/"+crime['rms_cdw_id']+".json"
            )
            for crime in crimes 
        ]
    
        if format is None:
            accept = self.request.headers.get('Accept').lower()
            if "application/rdf+xml" in accept:
                self.set_status(303)
                self.set_header("Location", self.base_uri + "/signs/" + id + ".rdf")
            else:
                self.set_status(303)
                self.set_header("Location", self.base_uri + "/signs/" + id + ".json")
        elif format == ".json":
            self.set_header("Content-Type", "application/json")
            self.write(json.dumps(filteredSign))
        elif format == ".rdf" or format == ".nt" or format == ".ttl":
            graph = ConjunctiveGraph()
            graph.bind('geo', GEO)
            graph.bind('dcterms', DCTERMS)
            graph.bind('yago', YAGO)
            graph.bind('parksafesign', PARKSAFESIGN)
            
            signURI = self.base_uri + "/signs/" + id
            
            graph.add((URIRef(signURI), RDF.type, YAGO['TrafficSigns']))
            graph.add((URIRef(signURI), GEO['lat'], Literal(filteredSign['latitude'])))
            graph.add((URIRef(signURI), GEO['lon'], Literal(filteredSign['longitude'])))
            graph.add((URIRef(signURI), PARKSAFESIGN['categoryDescription'], Literal(filteredSign['categoryde'])))
            graph.add((URIRef(signURI), PARKSAFESIGN['signText'], Literal(filteredSign['customtext'])))
            graph.add((URIRef(signURI), PARKSAFESIGN['blockInformation'], Literal(filteredSign['unitdesc'])))
            graph.add((URIRef(signURI), PARKSAFESIGN['starttime'], Literal(filteredSign['starttime'])))
            graph.add((URIRef(signURI), PARKSAFESIGN['endtime'], Literal(filteredSign['endtime'])))
            for crime in filteredSign['crimes']:
                graph.add((URIRef(signURI), PARKSAFESIGN['near'], URIRef(self.base_uri + "/crimes/" + crime['rms_cdw_id'])))
            
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
            

class QueryHandler(BaseHandler):
    def get(self):
        self.render("query.html")
        
        
class IndexHandler(BaseHandler):
    def get(self):
        self.render("index.html")