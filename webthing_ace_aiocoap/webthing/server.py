# Create implicit path.
import sys
from os import path, pardir

from webthing.utils import get_ip
sys.path.append(path.join(path.dirname(path.abspath(__file__)), pardir, pardir))

import asyncio
import aiocoap.resource

from webthing import SingleThing, MultipleThings



from webthing_ace_aiocoap.webthing.handlers import *


import socket


from zeroconf import ServiceInfo, Zeroconf



class CoapWebThingServer():
    """Server to represent a Web Thing over HTTP."""

    def __init__(self, things, port = 8086, hostname = None):
        """
        Initialize the WebThingServer.

        things -- things managed by this server.
          + should be of type SingleThing or MultipleThings
        port -- port to listen on (defaults to 80)\n
        hostname -- Optional host name, i.e. mything.com\n

        """
        self.things = things
        self.name = things.get_name()
        self.port = port
        self.hostname = hostname
        self.ip = get_ip()





        # Resource tree creation
        self.app = aiocoap.resource.Site()

        self.app.add_resource(('authz-info',),
                              AuthzHandler())
        self.app.add_resource(('.well-known', 'edhoc'),
                              EdhocHandler())

        # NOTE: As a workaround (' ',) is used instead of ('',). Usage of ('',) results in  4.04.
        coap_uri = (' ',)
        self.app.add_resource(coap_uri,
                              ThingsHandler(self.things,
                                            coap_uri))

        if isinstance(things, MultipleThings):

            for idx, thing in enumerate(self.things.get_things()):
                tdx = (str(idx),)

                coap_uri = tdx
                self.app.add_resource(coap_uri,
                                      ThingHandler(self.things,
                                                   coap_uri))
                self.make_handlers(tdx, thing)

        else:
            tdx = ()

            self.make_handlers(tdx, self.things.get_thing(0))







    def make_handlers(self, tdx, thing):


        coap_uri = tdx + ('properties',)
        self.app.add_resource(coap_uri,
                              PropertiesHandler(self.things,
                                                coap_uri))

        for property in thing.get_properties():
            coap_uri = tdx + ('properties', property)
            self.app.add_resource(coap_uri,
                                  PropertyHandler(self.things,coap_uri))

        coap_uri = tdx + ('actions',)
        self.app.add_resource(coap_uri,
                              ActionsHandler(self.things,
                                             coap_uri))

        for action_name in thing.available_actions:
            coap_uri = tdx + ('actions', action_name)
            self.app.add_resource(coap_uri,
                                  ActionHandler(self.things,coap_uri))

        # TODO:
        # Find a way to handle requests to action_ID.
        # This might be problematic because action_IDs are not actions,
        # but contents of queue for every action.
        # Thus they have a 'dynamic' nature.
        # This will also cause issues for 'scopes' defined in AS.


        coap_uri = tdx + ('events',)
        self.app.add_resource(coap_uri, EventsHandler(self.things,coap_uri))

        for event_name in thing.available_events:
            coap_uri = tdx + ('events', event_name)
            self.app.add_resource(coap_uri,EventHandler(self.things, coap_uri))




    def start(self):
        """Start listening for incoming connections."""
        self.service_info = ServiceInfo(type_ = '_webthing._udp.local.',
                                        name = '{}._webthing._udp.local.'.format(self.name),
                                        address = socket.inet_aton(self.ip),
                                        port = self.port,
                                        properties = {'path': '/', },
                                        server = '{}.local.'.format(socket.gethostname()))
        self.zeroconf = Zeroconf()
        self.zeroconf.register_service(self.service_info)

        asyncio.Task(aiocoap.Context.create_server_context(site = self.app,
                                                           bind = (self.hostname,
                                                                   self.port)))




        # Here would be a good point to generate an Event (if needed for prototyping).

        asyncio.get_event_loop().run_forever()







    def stop(self):
        """Stop listening."""
        self.zeroconf.unregister_service(self.service_info)
        self.zeroconf.close()
        asyncio.get_event_loop().stop()