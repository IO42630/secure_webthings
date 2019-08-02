# Create implicit path.
import sys
from os import path , pardir
sys.path.append(path.join(path.dirname(path.abspath(__file__)), pardir, pardir))


from aiocoap.numbers.codes import Code
import aiocoap.resource

import logging
from webthing.errors import PropertyError


from ace.cbor.constants import Keys
from ace.cose.constants import Key
from ace.cose.key import CoseKey
from ace.cose.cose import SignatureVerificationFailed


import ace.cose.cwt as cwt
from ace.rs.resource_server import ResourceServer, NotAuthorizedException



from cbor2 import dumps, loads


from webthing_ace_aiocoap.parameters import *


from webthing_ace_aiocoap.webthing.errors import *


class AceHandler(aiocoap.resource.Resource):
    """
    Extend PathCapable instead of Resource to support Path
    """
    # class variable
    # contains token_cache and edhoc_server
    # TODO replace *forbidden_thing*


    rs = ResourceServer(audience = AUDIENCE,
                        identity = RS_IDENTITY,
                        as_url = PI_AS_URL,
                        as_public_key = AS_PUBLIC_KEY)


class AuthzHandler(AceHandler):
    """
    Handle a request to ('authz-info',).\n
    CONTEXT: ('authz-info',) is the endpoint where the *Client* uploads the *Acess Token*
    before the establishment of the *Oscore Context* begins.
    """


    async def render_post(self, request):
        access_token: bytes = request.payload

        # introspect_payload = self.introspect(access_token)

        # Verify if valid CWT from AS
        try:
            decoded = cwt.decode(encoded = access_token,
                                 key = AceHandler.rs.as_public_key)

        except SignatureVerificationFailed:
            return aiocoap.Message(code = Code.UNAUTHORIZED)

        # Check if audience claim in token matches audience identifier of this resource server
        if decoded[Keys.AUD] != AceHandler.rs.audience:
            return aiocoap.Message(code = Code.FORBIDDEN)

        # Extract PoP CoseKey
        pop_key: CoseKey = CoseKey.from_cose(decoded[Keys.CNF][Key.COSE_KEY])

        # Store token and store by PoP key id
        AceHandler.rs.token_cache.add_token(token = decoded,
                                            pop_key_id = pop_key.key_id)

        # Inform EDHOC Server about new key
        AceHandler.rs.edhoc_server.add_peer_identity(key_id = pop_key.key_id,
                                                     key = pop_key.key)

        logging.info('AuthzInfo returning.')

        return aiocoap.Message(code = Code.CREATED)


class EdhocHandler(AceHandler):


    async def render_post(self, request):
        message = request.payload
        response = AceHandler.rs.edhoc_server.on_receive(message)
        return aiocoap.Message(code = Code.CREATED,
                               payload = bytes(response))




class BaseHandler(AceHandler):
    """
    Checks authorization.
    """
    def __init__(self, things, coap_uri):
        super().__init__()
        self.things = things
        self.coap_uri = coap_uri
        self.oscore_context = None


    async def render(self, request):

        def to_http(coap_uri: tuple) -> str:
            http_uri = ''
            for m in coap_uri:
                http_uri += '/' + str(m)
            return http_uri


        scope = str(request.code) + ' ' + to_http(self.coap_uri)
        prot, unprot, cipher = loads(request.payload).value
        try:
            self.oscore_context = AceHandler.rs.oscore_context(unprot, scope)
        except NotAuthorizedException:
            raise NotAuthorizedException
        else:
            return await super().render(request)




class BaseThingHandler(BaseHandler):
    """
    Prepares all that is associated with a thing, such as:
      + `self.thing_id`
      + the `self.thing is None` check
    """
    def __init__(self, things, coap_uri):
        super().__init__(things, coap_uri)
        self.thing_id = coap_uri[0]
        self.thing = None


    # TODO: It would be elegant to replace render_$ with render. Be careful to avoid the recursion error.
    # sync def render(self, request):
    #    """
    #    **render** delegates to **render_$**.
    #    See `aiocoap.resource.Resource()`.
    #    """
    #
    #    self.thing = self.things.get_thing(self.thing_id)
    #    if self.thing is None:
    #        raise ThingNotFoundException
    #    else:
    #        return await super().render(request)


    async def render_get(self, request):
        """
        Every `render_$` function is delegated by `.render()` in
        """
        self.set_and_check_thing()


    async def render_post(self, request):
        self.set_and_check_thing()


    async def render_put(self, request):
        self.set_and_check_thing()


    async def render_delete(self, request):
        self.set_and_check_thing()


    def set_and_check_thing(self):
        self.thing = self.things.get_thing(self.thing_id)
        if self.thing is None:
            raise ThingNotFoundException


class ThingsHandler(BaseHandler):


    async def render_get(self, request):
        """"""
        response = [thing.as_thing_description()
                    for idx, thing in enumerate(self.things.get_things())]
        return aiocoap.Message(payload = self.oscore_context.encrypt(dumps(response)))


class ThingHandler(BaseThingHandler):


    async def render_get(self, request):
        """
        This deviates from the WebThings spec, because WebSockets are not in scope of this project.
        STATUS:
          + DONE_
          + TODO_ test normal, test errors, add bonus error handlers.
        """
        try:
            await super().render(request)
        except NotAuthorizedException:
            return aiocoap.Message(code = Code.UNAUTHORIZED)
        except ThingNotFoundException:
            return aiocoap.Message(code = Code.NOT_FOUND)
        else:
            response = self.oscore_context.encrypt(dumps(self.thing.as_thing_description()))
            return aiocoap.Message(payload = response)


class PropertiesHandler(BaseThingHandler):
    """Handle a request to /properties."""


    async def render_get(self, request):
        """
        STATUS:
          + DONE_ match original, test normal
          + TODO_ , test errors, add bonus error handlers.
        """
        try:
            await super().render_get(request)
        except NotAuthorizedException:
            return aiocoap.Message(code = Code.UNAUTHORIZED)
        except ThingNotFoundException:
            return aiocoap.Message(code = Code.NOT_FOUND)
        else:
            response = self.oscore_context.encrypt(dumps(self.thing.get_properties()))
            return aiocoap.Message(payload = response)


class PropertyHandler(BaseThingHandler):
    """
    The`request` parameter has a `code` field, such as `GET`, `POST` and others.
    Supported codes: aiocoap.numbers.codes..
    diffrent from Tornado where  PropertyHandler.get() can have property as parameter,
    this is not advised in aiocoap,
    therefore in the spirit of REST everything will be done by the scope parameter.
    """


    def __init__(self, things, coap_uri):
        super().__init__(things, coap_uri)
        _ = self.coap_uri.index('properties')
        self.property_name = coap_uri[_ + 1]


    async def render_get(self, request):
        """
        STATUS:
          + DONE_ match original, test normal.
          + TODO_ test errors, add bonus error handlers.
        """
        try:
            await super().render_get(request)
        except NotAuthorizedException:
            return aiocoap.Message(code = Code.UNAUTHORIZED)
        except ThingNotFoundException:
            return aiocoap.Message(code = Code.NOT_FOUND)
        else:
            if self.thing.has_property(self.property_name):
                # NOTE: do not use `self.property` value, because that will always point at the original value.
                _property_value = self.thing.get_property(self.property_name)
                response = self.oscore_context.encrypt(dumps({self.property_name: _property_value}))
                _ = self.get_link_description()
                return aiocoap.Message(payload = response)
            else:
                return aiocoap.Message(code = Code.NOT_FOUND)


    async def render_post(self, request):
        """
        STATUS:
          + DONE_ match original, test normal.
          + TODO_ test errors, add bonus error handlers.
        """
        try:
            await super().render_post(request)
        except NotAuthorizedException:
            return aiocoap.Message(code = Code.UNAUTHORIZED)
        except ThingNotFoundException:
            return aiocoap.Message(code = Code.NOT_FOUND)
        else:
            try:
                args: dict = loads(self.oscore_context.decrypt(request.payload))
            except ValueError:
                return aiocoap.Message(code = Code.BAD_REQUEST)

            if self.property_name not in args:
                return aiocoap.Message(code = Code.BAD_REQUEST)

            if self.thing.has_property(self.property_name):
                try:
                    self.thing.set_property(self.property_name, args[self.property_name])
                except PropertyError:
                    return aiocoap.Message(code = Code.BAD_REQUEST)
                response = b'OK'
                return aiocoap.Message(payload = self.oscore_context.encrypt(dumps(response)))
            else:
                return aiocoap.Message(code = Code.NOT_FOUND)


class ActionsHandler(BaseThingHandler):
    """
    Handle GET or POST requests to /<thing_id>/actions .
    """


    async def render_get(self, request):
        """
        Return the description of the internal queue of actions.
        STATUS:
          + DONE_ match original,.
          + TODO_  test normal, test errors, add bonus error handlers.
        """
        try:
            await super().render_get(request)
        except NotAuthorizedException:
            return aiocoap.Message(code = Code.UNAUTHORIZED)
        except ThingNotFoundException:
            return aiocoap.Message(code = Code.NOT_FOUND)
        else:
            response = self.thing.get_action_descriptions()
            return aiocoap.Message(payload = self.oscore_context.encrypt(dumps(response)))


    async def render_post(self, request):
        """
        Add all supplied actions to the internal queue.\n
        As no action_name is supplied in URI,
        instead get all action_names from request.payload.\n
        The result is similar to `ActionHandler`,
        except no check to match a specific action is performed.
        STATUS:
          + DONE_ match original, test normal.
          + TODO_ test errors, add bonus error handlers.
        """
        try:
            await super().render_post(request)
        except NotAuthorizedException:
            return aiocoap.Message(code = Code.UNAUTHORIZED)
        except ThingNotFoundException:
            return aiocoap.Message(code = Code.NOT_FOUND)
        else:
            try:
                args: dict = loads(self.oscore_context.decrypt(request.payload))
            except ValueError:
                return aiocoap.Message(code = Code.BAD_REQUEST)

            response = {}
            for action_name, action_params in args.items():

                input_ = None
                if 'input' in action_params:
                    input_ = action_params['input']

                action = self.thing.perform_action(action_name, input_)
                if action:
                    response.update(action.as_action_description())
                    action.start()

            return aiocoap.Message(payload = self.oscore_context.encrypt(dumps(response)))


class ActionHandler(BaseThingHandler):
    """
    Handle GET or POST requests to /<thing_id>/actions/<action_name> .
    """
    def __init__(self, things, coap_uri):
        super().__init__(things, coap_uri)
        _ = self.coap_uri.index('actions')
        self.action_name = coap_uri[_ + 1]


    async def render_get(self, request):
        """
        Return the description of the internal queue of actions.
        Only consider the actions whose name is `action_name`.
        STATUS:
          + DONE_ match WT original, test normal.
          + TODO_ test errors, add bonus error handlers.
        """
        try:
            await super().render_get(request)
        except NotAuthorizedException:
            return aiocoap.Message(code = Code.UNAUTHORIZED)
        except ThingNotFoundException:
            return aiocoap.Message(code = Code.NOT_FOUND)
        else:
            response = self.thing.get_action_descriptions(action_name = self.action_name)
            return aiocoap.Message(payload = self.oscore_context.encrypt(dumps(response)))


    async def render_post(self, request):
        """
        Add action to the internal queue of actions.\n
        return -- status of action (.as_action_description)
        STATUS:
          + DONE_ match original, test normal.
          + TODO_ test errors, add bonus error handlers.
        """
        try:
            await super().render_post(request)
        except NotAuthorizedException:
            return aiocoap.Message(code = Code.UNAUTHORIZED)
        except ThingNotFoundException:
            return aiocoap.Message(code = Code.NOT_FOUND)
        else:
            try:
                args: dict = loads(self.oscore_context.decrypt(request.payload))
            except ValueError:
                return aiocoap.Message(code = Code.BAD_REQUEST)

            response = {}
            for name, action_params in args.items():
                if name != self.action_name:
                    continue

                input_ = None
                if 'input' in action_params:
                    input_ = action_params['input']

                action = self.thing.perform_action(name, input_)
                if action:
                    response.update(action.as_action_description())
                    action.start()

            return aiocoap.Message(payload = self.oscore_context.encrypt(dumps(response)))


class ActionIDHandler(BaseThingHandler):
    """
    Handle GET or PUT or DELETE requests to /<thing_id>/actions/<action_name>/<action_id> .
    """
    def __init__(self, things, hosts, coap_uri):
        super().__init__(things, hosts, coap_uri)
        _ = self.coap_uri.index('actions')
        self.action_name = coap_uri[_ + 1]
        self.action_id = coap_uri[_ + 2]



    async def render_get(self, request):
        """ """
        try:
            await super().render_get(request)
        except NotAuthorizedException:
            return aiocoap.Message(code = Code.UNAUTHORIZED)
        except ThingNotFoundException:
            return aiocoap.Message(code = Code.NOT_FOUND)
        else:
            action = self.thing.get_action(self.action_name, self.action_id)
            if action is None:
                return aiocoap.Message(code = Code.NOT_FOUND)
            response = action.as_action_description()
            return aiocoap.Message(payload = self.oscore_context.encrypt(dumps(response)))


    async def render_put(self, request):
        try:
            await super().render_put(request)
        except NotAuthorizedException:
            return aiocoap.Message(code = Code.UNAUTHORIZED)
        except ThingNotFoundException:
            return aiocoap.Message(code = Code.NOT_FOUND)
        else:
            response = '(200: Not yet defined in the spec.)'
            return aiocoap.Message(payload = self.oscore_context.encrypt(dumps(response)))


    async def render_delete(self, request):
        """ """
        try:
            await super().render_delete(request)
        except NotAuthorizedException:
            return aiocoap.Message(code = Code.UNAUTHORIZED)
        except ThingNotFoundException:
            return aiocoap.Message(code = Code.NOT_FOUND)
        else:
            if self.thing.remove_action(self.action_name, self.action_id):
                response = '(204: No Content)'
                return aiocoap.Message(payload = self.oscore_context.encrypt(dumps(response)))
            else:
                return aiocoap.Message(code = Code.NOT_FOUND)


class EventsHandler(BaseThingHandler):
    """
    Handle GET requests to /<thing_id>/events .
    """
    async def render_get(self, request):
        """ """
        try:
            await super().render_get(request)
        except NotAuthorizedException:
            return aiocoap.Message(code = Code.UNAUTHORIZED)
        except ThingNotFoundException:
            return aiocoap.Message(code = Code.NOT_FOUND)
        else:
            response = self.thing.get_event_descriptions()
            return aiocoap.Message(payload = self.oscore_context.encrypt(dumps(response)))



class EventHandler(BaseThingHandler):
    """
    Handle GET requests to /<thing_id>/events/<event_name> .
    """
    def __init__(self, things, coap_uri):
        super().__init__(things,  coap_uri)
        _ = self.coap_uri.index('events')
        self.event_name = coap_uri[_ + 1]


    async def render_get(self, request):
        """ """
        try:
            await super().render_get(request)
        except NotAuthorizedException:
            return aiocoap.Message(code = Code.UNAUTHORIZED)
        except ThingNotFoundException:
            return aiocoap.Message(code = Code.NOT_FOUND)
        else:
            response = self.thing.get_event_descriptions(event_name = self.event_name)
            return aiocoap.Message(payload = self.oscore_context.encrypt(dumps(response)))
