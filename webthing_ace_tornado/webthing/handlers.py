import logging

import json
from typing import Optional, Awaitable

import tornado.concurrent
import tornado.gen
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.websocket

from webthing.server import MultipleThings
from webthing.errors import PropertyError

from ace.cbor.constants import Keys
from ace.cose.constants import Key
from ace.cose.key import CoseKey
from ace.cose.cose import SignatureVerificationFailed

import ace.cose.cwt as cwt
from ace.rs.resource_server import ResourceServer, NotAuthorizedException

from cbor2 import dumps, loads

from webthing_ace_tornado.parameters import *


@tornado.gen.coroutine
def perform_action(action):
    """Perform an Action in a coroutine."""
    action.start()


class AceHandler(tornado.web.RequestHandler):

    # class variable
    # contains token_cache and edhoc_server
    ace_rs = ResourceServer(audience = AUDIENCE,
                            identity = RS_IDENTITY,
                            as_url = PC_AS_URL,
                            as_public_key = AS_PUBLIC_KEY)

    logging.basicConfig(
            level = 10,
            format = "%(asctime)s %(filename)s:%(lineno)s %(levelname)s %(message)s"
            )

    def data_received(self, chunk: bytes) -> Optional[Awaitable[None]]:
        # 'implement' all abstracts methods of super
        pass


class AuthzHandler(AceHandler):
    """Handle a request to /authz-info/."""

    def post(self):
        """

        """
        access_token = self.request.body

        # Verify if valid CWT from AS
        try:
            decoded = cwt.decode(access_token, key = AceHandler.ace_rs.as_public_key)
        except SignatureVerificationFailed as err:
            self.set_status(401)
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps([{'error': {'error': str(err)}}]))
            return

        # Check if audience claim in token matches audience identifier of this resource server
        if decoded[Keys.AUD] != AceHandler.ace_rs.audience:
            self.set_status(403)
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps([{'error': 'Audience mismatch'}]))
            return

        # Extract PoP CoseKey
        pop_key = CoseKey.from_cose(decoded[Keys.CNF][Key.COSE_KEY])

        # Store token and PoP key id
        AceHandler.ace_rs.token_cache.add_token(token = decoded, pop_key_id = pop_key.key_id)

        # Inform EDHOC Server about new key
        AceHandler.ace_rs.edhoc_server.add_peer_identity(pop_key.key_id, pop_key.key)

        self.set_status(201)


class EdhocHandler(AceHandler):

    def post(self):
        message = self.request.body
        response = AceHandler.ace_rs.edhoc_server.on_receive(message)
        logging.info('EDHOC message was received.')
        self.set_status(201)
        self.write(bytes(response))


class BaseHandler(AceHandler):
    """Base handler that is initialized with a thing."""

    def initialize(self, things, hosts):
        """
        Initialize the handler.

        things -- list of Things managed by this server
        hosts -- list of allowed hostnames
        """
        self.things = things
        self.hosts = hosts
        self.scope = self.request.method + ' ' + self.request.path

    def prepare(self):
        """Validate Host header."""
        host = self.request.headers.get('Host', None)
        if host is not None and host in self.hosts:
            return

        raise tornado.web.HTTPError(403)

    def get_thing(self, thing_id):
        """
        Get the thing this request is for.\n
        Returns the thing, or None if not found.\n
        :parameter thing_id: ID of the thing to get, in String form.
        """
        return self.things.get_thing(thing_id)

    def set_default_headers(self, *args, **kwargs):
        """Set the default headers for all requests."""
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Headers',
                        'Origin, X-Requested-With, Content-Type, Accept')
        self.set_header('Access-Control-Allow-Methods',
                        'GET, HEAD, PUT, POST, DELETE')

    def write_response(self, oscore_context, payload):
        """

        :param oscore_context:
        :param payload: Contains the message.
        :return:
        """
        self.set_header('Content-Type', 'application/cbor')
        cbor_data_dump = dumps(payload)
        response = oscore_context.encrypt(cbor_data_dump)
        self.write(response)


class ThingsHandler(BaseHandler):
    """Handle a request to / when the server manages multiple things."""
    # TODO : to test this swap example to MultipleThings
    def get(self):
        """ Handle a GET request. """
        prot, unprot, cipher = loads(self.request.body).value
        try:
            oscore_context = AceHandler.ace_rs.oscore_context(unprot, self.scope)
        except NotAuthorizedException:
            raise NotAuthorizedException

        self.set_header('Content-Type', 'application/json')
        cbor_data_dump = dumps([
            thing.as_thing_description()
            for idx, thing in enumerate(self.things.get_things())
            ])
        response = oscore_context.encrypt(cbor_data_dump)
        self.write(response)


class ThingHandler(BaseHandler):
    """Handle a request to /."""
    # TODO:  This omits all the WebSocket features in the Mozilla original.
    def get(self, thing_id = '0'):
        """ Handle a GET request. """
        try:
            # An unauthorized GET request will have *request.body == b''*,
            # thus *cbor2.loads()* will fail,
            # thus place the next line inside *try:*.
            prot, unprot, cipher = loads(self.request.body).value
            oscore_context = AceHandler.ace_rs.oscore_context(unprot, self.scope)
        except Exception as e:
            print(e)
            self.set_status(401)
            return

        self.write_response(oscore_context = oscore_context,
                            payload = self.get_thing(thing_id).as_thing_description())


class PropertiesHandler(BaseHandler):
    """
    Handles a request to /properties.
    Uses CBOR for loads/dumps of payload/body,
    different implementation with JSON possible.
    """
    def get(self, thing_id = '0'):
        """
        Handle a GET request.\n
        :parameter thing_id: ID of the thing this request is for.
        """
        thing = self.get_thing(thing_id)
        if thing is None:
            self.set_status(404)
            return

        try:
            # An unauthorized GET request will have *request.body == b''*,
            # thus *cbor2.loads()* will fail,
            # thus place the next line inside *try:*.
            prot, unprot, cipher = loads(self.request.body).value
            oscore_context = AceHandler.ace_rs.oscore_context(unprot, self.scope)
        except NotAuthorizedException:
            self.set_status(401)
            return

        self.write_response(oscore_context = oscore_context,
                            payload = thing.get_properties())


class PropertyHandler(BaseHandler):
    """Handle a request to /properties/<property>."""

    def get(self, thing_id = '0', property_name = None):
        """Handle a GET request."""
        thing = self.get_thing(thing_id)
        if thing is None:
            self.set_status(404)
            return

        prot, unprot, cipher = loads(self.request.body).value
        try:
            oscore_context = AceHandler.ace_rs.oscore_context(unprot, self.scope)
        except NotAuthorizedException:
            self.set_status(401)
            return

        if thing.has_property(property_name):
            self.write_response(oscore_context,
                                {property_name: thing.get_property(property_name)})
        else:
            self.set_status(404)

    def post(self, thing_id = '0', property_name = None):
        """
        Handle a PUT request.

        thing_id -- ID of the thing this request is for
        property_name -- the name of the property from the URL path
        """
        thing = self.get_thing(thing_id)
        if thing is None:
            self.set_status(404)
            return

        # uses CBOR for load/dump of payload/body, another implementation with JSON possible
        prot, unprot, cipher = loads(self.request.body).value
        try:
            oscore_context = AceHandler.ace_rs.oscore_context(unprot, self.scope)
        except NotAuthorizedException:
            self.set_status(401)
            return

        try:
            args = loads(oscore_context.decrypt(self.request.body))
            # translate keys from bytes to str
            _args = {}
            for k in args:
                _args.update({k.decode('utf-8'): args.get(k)})
            args = _args
        except ValueError:
            self.set_status(400)
            return

        if property_name not in args:
            self.set_status(400)
            return

        if thing.has_property(property_name):
            try:
                thing.set_property(property_name, args[property_name])
            except PropertyError:
                self.set_status(400)
                return
            # code matches ACE http-client : check if this deviation from Mozilla spec is necessary.
            self.set_status(201)
            self.write_response(oscore_context = oscore_context,
                                payload = {property_name: thing.get_property(property_name), })
        else:
            self.set_status(404)


class ActionsHandler(BaseHandler):
    """Handle a request to /actions."""

    def get(self, thing_id = '0'):
        """
        Handle a GET request.

        thing_id -- ID of the thing this request is for
        """
        thing = self.get_thing(thing_id)
        if thing is None:
            self.set_status(404)
            return

        # uses CBOR for load/dump of payload/body, another implementation with JSON possible
        prot, unprot, cipher = loads(self.request.body).value
        try:
            oscore_context = AceHandler.ace_rs.oscore_context(unprot, self.scope)
        except NotAuthorizedException:
            self.set_status(401)
            return

        self.write_response(oscore_context = oscore_context,
                            payload = thing.get_action_descriptions())

    def post(self, thing_id = '0'):
        """
        Handle a POST request.

        thing_id -- ID of the thing this request is for
        """
        thing = self.get_thing(thing_id)
        if thing is None:
            self.set_status(404)
            return

        # uses CBOR for load/dump of payload/body, another implementation with JSON possible
        prot, unprot, cipher = loads(self.request.body).value
        try:
            oscore_context = AceHandler.ace_rs.oscore_context(unprot, self.scope)
        except NotAuthorizedException:
            self.set_status(401)
            return
        ##

        try:
            args = loads(oscore_context.decrypt(self.request.body))
            # translate keys from bytes to str
            _args = {}
            for k in args:
                _args.update({k.decode('utf-8'): args.get(k)})
            args = _args
        except ValueError:
            self.set_status(400)
            return

        response = {}
        for action_name, action_params in args.items():
            input_ = None
            if 'input' in action_params:
                input_ = action_params['input']

            action = thing.perform_action(action_name, input_)
            if action:
                response.update(action.as_action_description())

                # Start the action
                tornado.ioloop.IOLoop.current().spawn_callback(
                        perform_action,
                        action,
                        )

        self.set_status(201)
        self.write(oscore_context.encrypt(dumps(response)))


class ActionHandler(BaseHandler):
    """Handle a request to /actions/<action_name>."""

    def get(self, thing_id = '0', action_name = None):
        """
        Handle a GET request.

        thing_id -- ID of the thing this request is for
        action_name -- name of the action from the URL path
        """
        thing = self.get_thing(thing_id)
        if thing is None:
            self.set_status(404)
            return

        # uses CBOR for load/dump of payload/body, another implementation with JSON possible
        prot, unprot, cipher = loads(self.request.body).value
        try:
            self.oscore_context = AceHandler.ace_rs.oscore_context(unprot, self.scope)
        except NotAuthorizedException:
            self.set_status(401)
            return
        ##


        self.set_header('Content-Type', 'application/cbor')
        cbor_data_dump = dumps(thing.get_action_descriptions(action_name = action_name))
        response = self.oscore_context.encrypt(cbor_data_dump)
        self.write(response)


    def post(self, thing_id = '0', action_name = None):
        """
        Handle a POST request.

        thing_id -- ID of the thing this request is for
        """
        thing = self.get_thing(thing_id)
        if thing is None:
            self.set_status(404)
            return

        # uses CBOR for load/dump of payload/body, another implementation with JSON possible
        prot, unprot, cipher = loads(self.request.body).value
        try:
            self.oscore_context = AceHandler.ace_rs.oscore_context(unprot, self.scope)
        except NotAuthorizedException:
            self.set_status(401)
            return
        ##

        try:
            args = loads(self.oscore_context.decrypt(self.request.body))
            # translate keys from bytes to str
            _args = {}
            for k in args:
                _args.update({k.decode('utf-8'): args.get(k)})
            args = _args
        except ValueError:
            self.set_status(400)
            return

        response = {}
        for name, action_params in args.items():
            if name != action_name:
                continue

            input_ = None
            if 'input' in action_params:
                input_ = action_params['input']

            action = thing.perform_action(name, input_)
            if action:
                response.update(action.as_action_description())

                # Start the action
                tornado.ioloop.IOLoop.current().spawn_callback(
                        perform_action,
                        action,
                        )

        self.set_status(201)
        self.write(self.oscore_context.encrypt(dumps(response)))


class ActionIDHandler(BaseHandler):
    """Handle a request to /actions/<action_name>/<action_id>."""

    def get(self, thing_id = '0', action_name = None, action_id = None):
        """
        Handle a GET request.

        thing_id -- ID of the thing this request is for
        action_name -- name of the action from the URL path
        action_id -- the action ID from the URL path
        """
        thing = self.get_thing(thing_id)
        if thing is None:
            self.set_status(404)
            return

        # uses CBOR for load/dump of payload/body, another implementation with JSON possible
        prot, unprot, cipher = loads(self.request.body).value
        try:
            self.oscore_context = AceHandler.ace_rs.oscore_context(unprot, self.scope)
        except NotAuthorizedException:
            self.set_status(401)
            return
        ##

        action = thing.get_action(action_name, action_id)
        if action is None:
            self.set_status(404)
            return

        self.set_header('Content-Type', 'application/cbor')
        cbor_data_dump = dumps(action.as_action_description())
        response = self.oscore_context.encrypt(cbor_data_dump)
        self.write(response)


    def put(self, thing_id = '0', action_name = None, action_id = None):
        """
        Handle a PUT request.

        TODO: this is not yet defined in the spec

        thing_id -- ID of the thing this request is for
        action_name -- name of the action from the URL path
        action_id -- the action ID from the URL path
        """
        thing = self.get_thing(thing_id)
        if thing is None:
            self.set_status(404)
            return

        self.set_status(200)

    def delete(self, thing_id = '0', action_name = None, action_id = None):
        """
        Handle a DELETE request.

        thing_id -- ID of the thing this request is for
        action_name -- name of the action from the URL path
        action_id -- the action ID from the URL path
        """
        thing = self.get_thing(thing_id)
        if thing is None:
            self.set_status(404)
            return

        # uses CBOR for load/dump of payload/body, another implementation with JSON possible
        prot, unprot, cipher = loads(self.request.body).value
        try:
            self.oscore_context = AceHandler.ace_rs.oscore_context(unprot, self.scope)
        except NotAuthorizedException:
            self.set_status(401)
            return
        ##


        if thing.remove_action(action_name, action_id):
            self.set_status(204)
        else:
            self.set_status(404)


class EventsHandler(BaseHandler):
    """Handle a request to /events."""

    def get(self, thing_id = '0'):
        """
        Handle a GET request.

        thing_id -- ID of the thing this request is for
        """
        thing = self.get_thing(thing_id)
        if thing is None:
            self.set_status(404)
            return

        # uses CBOR for load/dump of payload/body, another implementation with JSON possible
        prot, unprot, cipher = loads(self.request.body).value
        try:
            self.oscore_context = AceHandler.ace_rs.oscore_context(unprot, self.scope)
        except NotAuthorizedException:
            self.set_status(401)
            return
        ##



        self.set_header('Content-Type', 'application/cbor')
        cbor_data_dump = dumps(thing.get_event_descriptions())
        response = self.oscore_context.encrypt(cbor_data_dump)
        self.write(response)


class EventHandler(BaseHandler):
    """Handle a request to /events/<event_name>."""

    def get(self, thing_id = '0', event_name = None):
        """
        Handle a GET request.

        thing_id -- ID of the thing this request is for
        event_name -- name of the event from the URL path
        """
        thing = self.get_thing(thing_id)
        if thing is None:
            self.set_status(404)
            return

        # uses CBOR for load/dump of payload/body, another implementation with JSON possible
        prot, unprot, cipher = loads(self.request.body).value
        try:
            self.oscore_context = AceHandler.ace_rs.oscore_context(unprot, self.scope)
        except NotAuthorizedException:
            self.set_status(401)
            return

        self.set_header('Content-Type', 'application/cbor')
        cbor_data_dump = dumps(thing.get_event_descriptions(event_name = event_name))
        response = self.oscore_context.encrypt(cbor_data_dump)
        self.write(response)
