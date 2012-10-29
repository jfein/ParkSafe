import os
import json

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

from tornado.options import define, options

import handlers


define("port", default=8888, help="run on the given port", type=int)


class WebService(tornado.web.Application):
    """The Movie Service Web Application"""
    def __init__(self):
        h = [
			(r"/", handlers.HomeHandler),
            (r"/crimes.json", handlers.CrimesHandler),
            (r"/signs.json", handlers.SignsHandler),
        ]
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            debug=True,
            autoescape=None,
        )
        tornado.web.Application.__init__(self, h, **settings)
    

def main():
    tornado.options.parse_command_line()
    
    # Set up the Web application, pass the database
    service = WebService()
    
    # Set up HTTP server, pass Web application
    try:
        http_server = tornado.httpserver.HTTPServer(service)
        http_server.listen(options.port)
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        print "\nStopping service gracefully..."
    finally:
        tornado.ioloop.IOLoop.instance().stop()

        
if __name__ == "__main__":
    main()