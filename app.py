#!/usr/bin/env python

import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'vendor', 'lib', 'python'))

#
#  Really starting things here...
#
import tornado.ioloop
import tornado.httpserver
import tornado.web
from tornado.options import define, options

define("debug", default=False, help="run in debug mode", type=bool)
define("prefork", default=False, help="pre-fork across all CPUs", type=bool)
define("port", default=9000, help="run on the given port", type=int)
define("bootstrap", default=False, help="Run the bootstrap model commands")

from sample.web import MainHandler, ChatHandler
from backsync import BacksyncRouter
from sample import models

#
#
#
class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler),
            (r"/chatty", ChatHandler)
        ]

        BacksyncRouter.apply_routes(handlers)

        app_settings = dict(
            debug=options.debug,
            template_path=os.path.join(os.path.dirname(__file__), "sample", "web", "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "sample", "web", "static"),
        )

        super(Application, self).__init__(handlers, **app_settings)

        # self.channel = BacksyncChannel
        self.ioloop  = tornado.ioloop.IOLoop.instance()

def main():
    tornado.options.parse_command_line()

    app      = Application()

    http_server = tornado.httpserver.HTTPServer(app)

    print "Starting tornado on port", options.port
    if options.prefork:
        print "\tpre-forking"
        http_server.bind(options.port)
        http_server.start()
    else:
        http_server.listen(options.port)

    try:
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
