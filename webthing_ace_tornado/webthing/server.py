"""
Python Web Thing server implementation.
"""

from zeroconf import ServiceInfo, Zeroconf
import socket
import tornado.concurrent
import tornado.gen
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.websocket
from webthing.server import MultipleThings
from webthing.utils import get_ip

from webthing_ace_tornado.webthing.handlers import *


class AceWebThingServer:
    """Server to represent a Web Thing over HTTP."""

    def __init__(self, things, port = 80, hostname = None, ssl_options = None):
        """
        Initialize the WebThingServer.

        things -- things managed by this server -- should be of type
                  SingleThing or MultipleThings
        port -- port to listen on (defaults to 80)
        hostname -- Optional host name, i.e. mything.com
        ssl_options -- dict of SSL options to pass to the tornado server
        """
        self.things = things
        self.name = things.get_name()
        self.port = port
        self.hostname = hostname
        self.ip = get_ip()

        system_hostname = socket.gethostname()
        self.hosts = [
            '127.0.0.1',
            '127.0.0.1:{}'.format(self.port),
            'localhost',
            'localhost:{}'.format(self.port),
            self.ip,
            '{}:{}'.format(self.ip, self.port),
            '{}.local'.format(system_hostname),
            '{}.local:{}'.format(system_hostname, self.port),
            ]

        if self.hostname is not None:
            self.hosts.extend([
                self.hostname,
                '{}:{}'.format(self.hostname, self.port),
                ])

        if isinstance(self.things, MultipleThings):
            for idx, thing in enumerate(self.things.get_things()):
                thing.set_href_prefix('/{}'.format(idx))

            handlers = [
                (
                    r'/?',
                    ThingsHandler,
                    dict(things = self.things, hosts = self.hosts),
                    ),
                (
                    r'/(?P<thing_id>\d+)/?',
                    ThingHandler,
                    dict(things = self.things, hosts = self.hosts),
                    ),
                (
                    r'/(?P<thing_id>\d+)/properties/?',
                    PropertiesHandler,
                    dict(things = self.things, hosts = self.hosts),
                    ),
                (
                    r'/(?P<thing_id>\d+)/properties/' +
                    r'(?P<property_name>[^/]+)/?',
                    PropertyHandler,
                    dict(things = self.things, hosts = self.hosts),
                    ),
                (
                    r'/(?P<thing_id>\d+)/actions/?',
                    ActionsHandler,
                    dict(things = self.things, hosts = self.hosts),
                    ),
                (
                    r'/(?P<thing_id>\d+)/actions/(?P<action_name>[^/]+)/?',
                    ActionHandler,
                    dict(things = self.things, hosts = self.hosts),
                    ),
                (
                    r'/(?P<thing_id>\d+)/actions/' +
                    r'(?P<action_name>[^/]+)/(?P<action_id>[^/]+)/?',
                    ActionIDHandler,
                    dict(things = self.things, hosts = self.hosts),
                    ),
                (
                    r'/(?P<thing_id>\d+)/events/?',
                    EventsHandler,
                    dict(things = self.things, hosts = self.hosts),
                    ),
                (
                    r'/(?P<thing_id>\d+)/events/(?P<event_name>[^/]+)/?',
                    EventHandler,
                    dict(things = self.things, hosts = self.hosts),
                    ),
                (
                    r'/authz-info',
                    AuthzHandler,
                    ),
                (
                    r'/.well-known/edhoc',
                    EdhocHandler,
                    ),
                ]
        else:
            # If SingleThing
            handlers = [(r'/?',
                         ThingHandler,
                         dict(things = self.things, hosts = self.hosts),
                         ),
                        (r'/properties/?',
                         PropertiesHandler,
                         dict(things = self.things, hosts = self.hosts),
                         ),
                        (r'/properties/(?P<property_name>[^/]+)/?',
                         PropertyHandler,
                         dict(things = self.things, hosts = self.hosts),
                         ),
                        (r'/actions/?',
                         ActionsHandler,
                         dict(things = self.things, hosts = self.hosts),
                         ),
                        (r'/actions/(?P<action_name>[^/]+)/?',
                         ActionHandler,
                         dict(things = self.things, hosts = self.hosts),
                         ),
                        (r'/actions/(?P<action_name>[^/]+)/(?P<action_id>[^/]+)/?',
                         ActionIDHandler,
                         dict(things = self.things, hosts = self.hosts),
                         ),
                        (r'/events/?',
                         EventsHandler,
                         dict(things = self.things, hosts = self.hosts),
                         ),
                        (r'/events/(?P<event_name>[^/]+)/?',
                         EventHandler,
                         dict(things = self.things, hosts = self.hosts),
                         ),
                        (r'/authz-info/?',
                         AuthzHandler,
                         ),
                        (r'/.well-known/edhoc/?',
                         EdhocHandler,
                         ),
                        ]

        self.app = tornado.web.Application(handlers)
        self.app.is_tls = ssl_options is not None
        self.server = tornado.httpserver.HTTPServer(self.app,
                                                    ssl_options = ssl_options)

    def start(self):
        """Start listening for incoming connections."""
        self.service_info = ServiceInfo(type_ = '_webthing._tcp.local.',
                                        name = '{}._webthing._tcp.local.'.format(self.name),
                                        address = socket.inet_aton(self.ip),
                                        port = self.port,
                                        properties = {'path': '/', },
                                        server = '{}.local.'.format(socket.gethostname()))
        self.zeroconf = Zeroconf()
        self.zeroconf.register_service(self.service_info)

        self.server.listen(self.port)
        tornado.ioloop.IOLoop.current().start()

    def stop(self):
        """Stop listening."""
        self.zeroconf.unregister_service(self.service_info)
        self.zeroconf.close()
        self.server.stop()
