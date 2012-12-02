import httplib
import json
import time

conns = {}

class SoClient:
    '''
    Client class to interface with a socrata data source.
    Not threadsafe.
    '''

    def __init__(self, host, view_id):
        self.host = host
        self.view_id = view_id
        self.cols = self._get_columns()
        
    def get_conn(self):
        global conns
        if self.host not in conns:
            conns[self.host] = httplib.HTTPConnection(self.host)
        return conns[self.host]
        
    def remove_conn(self):
        global conns
        del(conns[self.host])
        
    # Calls socrata API
    # Will crash if error
    def _call_api(
            self,
            method,
            uri,
            data={},
            headers={}):
        try:
            conn = self.get_conn()
            
            jsonData = json.dumps(data)
            conn.request(method, uri, jsonData, headers)
            
            response = conn.getresponse()
            if response.reason != 'OK':
                print "There was an error detected."
                print "Response status = %s.\n" % response.status
                print "Response reason = %s.\n" % response.reason
                print "Response = %s.\n" % response.read()
                raise SystemExit(1)
                
            rawResponse = response.read()
            return json.loads(rawResponse)
        except:
            print "FUCKED UP"
            self.remove_conn()
            time.sleep(50)
            self._call_api(method, uri, data, headers)
            

    def _get_columns(self):
        return self._call_api(
            method="GET",
            uri="/api/views/" + self.view_id + "/columns.json"
        ) 
        
    def _get_col_id(self, name):
        for col in self.cols:
            if col["fieldName"] == name:
                return col["id"]
                
    def _get_col_keys(self):
        return [ col['fieldName'] for col in self.cols ]        
              
    # Run query, returns parsed & formatted data
    def query(self, condition):
        res = self._call_api(
            method="POST",
            uri="/views/INLINE/rows.json?method=index",
            headers={ "Content-type:" : "application/json" },
            data={
                "originalViewId" : self.view_id,
                "name" : "SoClient Inline Filter",
                "columns" : self.cols,
                "query" : { "filterCondition" : condition }
            }
        )
        
        rows = res["data"]
        if not rows:
            return []

        data = []
        keys = self._get_col_keys()
        start_key = len(rows[0]) - len(keys)
        for row in rows:
            obj = {}
            for i, key in enumerate(keys):
                obj[key] = row[i + start_key]
            data.append(obj)
        return data
       
    '''
    Methods to generate conditional terms for querying
    '''
    
    def AND(self, *args):
        return {
            "type" : "operator",
            "value" : "AND",
            "children" : args
        }
        
    def OR(self, *args):
        return {
            "type" : "operator",
            "value" : "OR",
            "children" : args
        }
         
    def EQUALS(self, *args):
        return {
            "type" : "operator",
            "value" : "EQUALS",
            "children" : args
        }
        
    def NOT_EQUALS(self, *args):
        return {
            "type" : "operator",
            "value" : "NOT_EQUALS",
            "children" : args
        }
        
    def CONTAINS(self, *args):
        return {
            "type" : "operator",
            "value" : "CONTAINS",
            "children" : args
        }

    def GREATER_THAN(self, *args):
        return {
            "type" : "operator",
            "value" : "GREATER_THAN",
            "children" : args
        }    
        
    def GREATER_THAN_OR_EQUALS(self, *args):
        return {
            "type" : "operator",
            "value" : "GREATER_THAN_OR_EQUALS",
            "children" : args
        }    
        
    def LESS_THAN(self, *args):
        return {
            "type" : "operator",
            "value" : "LESS_THAN",
            "children" : args
        }     
        
    def LESS_THAN_OR_EQUALS(self, *args):
        return {
            "type" : "operator",
            "value" : "LESS_THAN_OR_EQUALS",
            "children" : args
        }     
        
    def VAL(self, val):
        return {
            "type" : "literal",
            "value" : val
        }

    def COL(self, name):
        return { 
            "columnId" : self._get_col_id(name),
            "type" : "column"
        }
        
    def CIRCLE(self, col, lat, lon, r):
        return {
            "type" : "operator",
            "value" : "WITHIN_CIRCLE",
            "children" : [
                self.COL(col),
                self.VAL(lat),
                self.VAL(lon),
                self.VAL(r)
            ]
        }