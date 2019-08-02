import json
import logging
import threading
import time
import traceback

import aiohttp
import asyncio

from ace.client.coap import CoAPClient
from aiocoap import Context

from pkg.utils.utils import multi_loads, StoppableThread
import cbor2
from gateway_addon import Device, Action, Event

from ace.client.http import HTTPClient

from pkg.property import AceProperty

# imports parameters.py
from pkg.parameters import *

from jsonschema import validate
from jsonschema.exceptions import ValidationError




_POLL_INTERVAL = 5


class PollDevice(Device):

    def __init__(self, adapter, _id):
        super().__init__(adapter, _id)
        # stop_event is args of target == poll
        self.stop_event = threading.Event()
        self.polling_thread = threading.Thread(target = self.poll, args = (self.stop_event,))
        self.polling_thread.daemon = True
        self.polling_thread.start()

        self.events = []



    def poll(self, stop_event):
        while not stop_event.wait(1):
            time.sleep(_POLL_INTERVAL)
            try:
                self.update()

                logging.info('Device : ' + multi_loads(self.name) + ' was polled.')
            except Exception as e:
                logging.info('Polling failed:  ' + str(e))
                continue

    def update(self):
        """
        DO implement in child class.
        """
        pass


    def properties_update(self, thing_state, properties_state):
        for property_name in properties_state:
            # NOTE:
            # - description must be dict and corespond to property.metadata, not property.metadata.description.
            # - super.properties is a dict of with type { str : Property }
            # - property == None if dict entry does not exist.
            property = self.properties.get(property_name)
            if property is None:
                property = AceProperty(device = self,
                                       name = property_name,
                                       description = thing_state['properties'][property_name],
                                       value = properties_state[property_name])
                self.properties[property.name] = property
            else:
                property.update(value = properties_state[property_name])


    def events_update(self, events_state):
        for event_description in events_state:
            if event_description not in self.events:
                self.events.append(event_description)




class URLDevice(PollDevice):

    def __init__(self, adapter, _id, url):

        super().__init__(adapter, _id)
        print(BLUE + 'URLDevice().__init__()' + ENDC)
        self.url = url
        self.update()




    def get_property(self, property_name):
        """
        Gets Property from Self, thus from Device, thus without querying the real Thing
        """
        # TODO this is never used, set this to be used in amproxy, better even find how others use it.
        print(WARNING + 'ace_adapter.device.GET_property: ' + property_name + ENDC)
        super().get_property(property_name = property_name)



    def set_property(self, property_name, value):
        """
        """
        print(WARNING + 'ace_adapter.device.SET_property: ' + property_name + ' to ' + str(value) + ENDC)
        prop = self.find_property(property_name)
        if not prop:
            return

        try:
            _response = self.aiohttp_request(method = 'PUT',
                                             url = self.url + prop.description['links'][0]['href'],
                                             headers = {'Accept': 'application/json'},
                                             data = json.dumps({property_name: value})
                                             )
            print('Response: ' + str(_response))
        except Exception as e:
            print(FAIL + str(e) + ENDC)
        else:
            prop.set_value(value)



    def request_action(self, action_id, action_name, action_input):
        """
        This Overwrite is required because Parent would call its own *perform_action()* which is *pass*.
        """
        print(FAIL + 'INFO action is being requested' + ENDC)
        if action_name not in self.actions:
            return

        # Validate action input, if present.
        metadata = self.actions[action_name]
        if 'input' in metadata:
            try:
                validate(action_input, metadata['input'])
            except ValidationError:
                return
        print(FAIL + 'action_id' + str(action_id) + ENDC)
        print(FAIL + 'action_name' + str(action_name) + ENDC)
        print(FAIL + 'action_input' + str(action_input) + ENDC)
        action = Action(action_id, self, action_name, action_input)
        self.perform_action(action)



    def perform_action(self, action):
        print(FAIL + 'INFO action is being performed' + ENDC)
        try:
            _response: dict = self.aiohttp_request(method = 'POST',
                                                   url = self.url + '/actions/' + action.name,
                                                   headers = {'Accept': 'application/json'},
                                                   data = json.dumps({action.name: {'input': action.input}})
                                                   )
            print('Response:' + _response['content'].decode('utf-8'))
        except Exception as e:
            print(FAIL + str(e) + ENDC)




    def update(self):
        """
            Read from polled states *thing_state* and *property_state* into *self*.
            - ..._response: { 'status' : int, 'content' : str}
            - multi_loads will fail if unauthorized (status 401) .
            - properties_response needed because thing_response lacks Property Values.
        """
        thing_state = self.aiohttp_request(method = 'GET', url = self.url + '/')
        properties_state = self.aiohttp_request(method = 'GET', url = self.url + '/properties')
        events_state = self.aiohttp_request(method = 'GET', url = self.url + '/events')

        self.name = thing_state['name']
        self.description = thing_state['description']
        self.properties_update(thing_state, properties_state)
        self.actions.update(thing_state['actions'])
        self.events_update(events_state)



    def aiohttp_request(self, method, url, headers = None, data = None) -> bytes:
        """
            Performs requests through an aiohttp-client.
            Intended to communicate between the add-on and a Thing.
        """
        async def request():
            _session = aiohttp.ClientSession()
            response = None

            if method == 'GET':
                response = await _session.get(url)
            elif method == 'PUT':
                response = await _session.put(url, headers = headers, data = data)
            elif method == 'POST':
                response = await _session.post(url, headers = headers, data = data)

            try:
                response_content = await response.read()
            except Exception:
                response_content = b''

            await _session.close()

            return multi_loads(response_content)

        return asyncio.new_event_loop().run_until_complete(request())





class AceURLDevice(PollDevice):


    def __init__(self, adapter, _id, url):

        super().__init__(adapter, _id)
        print(BLUE + 'AceThingURLDevice().__init__()' + ENDC)
        self.url = url

        self.ace_session = self.request_acess_token()
        self.upload_access_token()

        self.update()




    def get_property(self, property_name):
        """
            Gets Property from Self, thus from Device, thus without querying the real Thing
        """
        # TODO this is never used, set this to be used in amproxy, better even find how others use it.
        print(WARNING + 'ace_adapter.device.GET_property: ' + property_name + ENDC)
        super().get_property(property_name = property_name)




    def set_property(self, property_name, value):
        """
            Sets a property via ACE HTTP client.
        """
        print(WARNING + 'ace_adapter.device.SET_property: ' + property_name + ' to ' + str(value) + ENDC)
        prop = self.find_property(property_name)
        if not prop:
            return

        async def request(ace_session, url):
            # TODO
            client = HTTPClient(client_id = CLIENT_ID,
                                client_secret = CLIENT_SECRET
                                )
            data = cbor2.dumps({bytes(property_name, 'utf-8'): value})
            response = await client.post_resource(session = ace_session,
                                                  rs_url = url,
                                                  endpoint = '/properties/' + property_name,
                                                  data = data)
            return response

        try:
            asyncio.new_event_loop().run_until_complete(request(self.ace_session, self.url))
        except Exception as e:
            print(FAIL + str(e) + ENDC)
        else:
            prop.set_value(value)



    def request_action(self, action_id, action_name, action_input):
        """
        This Overwrite is required because Parent would call its own *perform_action()* which is *pass*.
        """
        print(FAIL + 'INFO action is being requested' + ENDC)
        if action_name not in self.actions:
            return

        # Validate action input, if present.
        metadata = self.actions[action_name]
        if 'input' in metadata:
            try:
                validate(action_input, metadata['input'])
            except ValidationError:
                return
        print(FAIL + 'action_id' + str(action_id) + ENDC)
        print(FAIL + 'action_name' + str(action_name) + ENDC)
        print(FAIL + 'action_input' + str(action_input) + ENDC)
        action = Action(action_id, self, action_name, action_input)
        self.perform_action(action)

    def perform_action(self, action):
        print(FAIL + 'INFO action is being performed' + ENDC)
        async def request(ace_session, url):
            client = HTTPClient(client_id = CLIENT_ID,
                                client_secret = CLIENT_SECRET
                                )
            data = cbor2.dumps({bytes(action.name, 'utf-8'): {'input': action.input}})
            response = await client.post_resource(session = ace_session,
                                                  rs_url = url,
                                                  endpoint = '/actions/' + action.name,
                                                  data = data)
            return response

        try:
            asyncio.new_event_loop().run_until_complete(request(self.ace_session, self.url))
        except Exception as e:
            print(FAIL + str(e) + ENDC)





    def update(self):

        async def request_thing(ace_session, url):
            client = HTTPClient(client_id = CLIENT_ID,
                                client_secret = CLIENT_SECRET
                                )
            thing_response = await client.access_resource(session = ace_session,
                                                          rs_url = url,
                                                          endpoint = '/')
            return multi_loads(thing_response)



        async def request_properties(ace_session, url):
            client = HTTPClient(client_id = CLIENT_ID,
                                client_secret = CLIENT_SECRET
                                )
            properties_response = await client.access_resource(session = ace_session,
                                                               rs_url = url,
                                                               endpoint = '/properties')
            return multi_loads(properties_response)



        async def request_events(ace_session, url):
            client = HTTPClient(client_id = CLIENT_ID,
                                client_secret = CLIENT_SECRET
                                )
            events_response = await client.access_resource(session = ace_session,
                                                           rs_url = url,
                                                           endpoint = '/events')
            return multi_loads(events_response)


        thing_state = asyncio.new_event_loop().run_until_complete(request_thing(self.ace_session, self.url))
        properties_state = asyncio.new_event_loop().run_until_complete(request_properties(self.ace_session, self.url))
        events_state = asyncio.new_event_loop().run_until_complete(request_events(self.ace_session, self.url))

        self.name = thing_state['name']
        self.description = thing_state['description']
        self.properties_update(thing_state, properties_state)
        self.actions.update(thing_state['actions'])
        self.events_update(events_state)




    def request_acess_token(self):

        async def request():
            client = HTTPClient(client_id = CLIENT_ID,
                                client_secret = CLIENT_SECRET
                                )

            ace_session = await client.request_access_token(as_url = AS_URL,
                                                            audience = AUDIENCE,
                                                            scopes = SCOPES
                                                            )
            return ace_session

        return asyncio.new_event_loop().run_until_complete(request())




    def upload_access_token(self):

        async def request(ace_session, url):
            client = HTTPClient(client_id = CLIENT_ID,
                                client_secret = CLIENT_SECRET
                                )

            await client.upload_access_token(session = ace_session,
                                             rs_url = url,
                                             endpoint = '/authz-info')


        asyncio.new_event_loop().run_until_complete(request(self.ace_session, self.url))




class CoapAceURLDevice(PollDevice):


    def __init__(self, adapter, _id, url):

        super().__init__(adapter, _id)
        print(BLUE + 'AceThingURLDevice().__init__()' + ENDC)
        self.url = url

        self.ace_session = self.request_acess_token()
        self.upload_access_token()

        self.update()





    def get_property(self, property_name):
        """
            Gets Property from Self, thus from Device, thus without querying the real Thing
        """
        # TODO this is never used, set this to be used in amproxy, better even find how others use it.
        print(WARNING + 'ace_adapter.device.GET_property: ' + property_name + ENDC)
        super().get_property(property_name = property_name)




    def set_property(self, property_name, value):
        """
        Set a property value.

        property_name -- name of the property to set
        value -- value to set
        """
        print(WARNING + 'ace_adapter.device.SET_property: ' + property_name + ' to ' + str(value) + ENDC)
        prop = self.find_property(property_name)
        if not prop:
            return

        async def request(ace_session, url):
            protocol = await Context.create_client_context()
            client = CoAPClient(client_id = CLIENT_ID,
                                client_secret = CLIENT_SECRET,
                                protocol = protocol
                                )
            data = cbor2.dumps({property_name: value})
            response = await client.post_resource(session = ace_session,
                                                  rs_url = url,
                                                  endpoint = '/properties/' + property_name,
                                                  data = data)
            return response

        # TODO adjust for multipleThings
        try:
            asyncio.new_event_loop().run_until_complete(request(self.ace_session, self.url))
        except Exception as e:
            print(FAIL + str(e) + ENDC)
        else:
            prop.set_value(value)


    def request_action(self, action_id, action_name, action_input):
        """
        This Overwrite is required because Parent would call its own *perform_action()* which is *pass*.
        """
        print(FAIL + 'INFO action is being requested' + ENDC)
        if action_name not in self.actions:
            return

        # Validate action input, if present.
        metadata = self.actions[action_name]
        if 'input' in metadata:
            try:
                validate(action_input, metadata['input'])
            except ValidationError:
                return
        print(FAIL + 'action_id' + str(action_id) + ENDC)
        print(FAIL + 'action_name' + str(action_name) + ENDC)
        print(FAIL + 'action_input' + str(action_input) + ENDC)
        action = Action(action_id, self, action_name, action_input)
        self.perform_action(action)

    def perform_action(self, action):
        print(FAIL + 'INFO action is being performed' + ENDC)
        async def request(ace_session, url):
            protocol = await Context.create_client_context()
            client = CoAPClient(client_id = CLIENT_ID,
                                client_secret = CLIENT_SECRET,
                                protocol = protocol
                                )
            data = cbor2.dumps({action.name: {'input': action.input}})
            response = await client.post_resource(session = ace_session,
                                                  rs_url = url,
                                                  endpoint = '/actions/' + action.name,
                                                  data = data)
            return response

        try:
            asyncio.new_event_loop().run_until_complete(request(self.ace_session, self.url))
        except Exception as e:
            print(FAIL + str(e) + ENDC)




    def cancel_action(self, action_id, action_name):
        # TODO add ~ here
        super().cancel_action(action_id, action_name)





    def update(self):


        async def request_thing(ace_session):
            protocol = await Context.create_client_context()
            client = CoAPClient(client_id = CLIENT_ID,
                                client_secret = CLIENT_SECRET,
                                protocol = protocol
                                )
            thing_response = await client.access_resource(session = ace_session,
                                                       rs_url = self.url,
                                                       endpoint = '/ ')
            return multi_loads(thing_response[0])

        async def request_properties(ace_session):
            protocol = await Context.create_client_context()
            client = CoAPClient(client_id = CLIENT_ID,
                                client_secret = CLIENT_SECRET,
                                protocol = protocol
                                )
            properties_response = await client.access_resource(session = ace_session,
                                                            rs_url = self.url,
                                                            endpoint = '/properties')
            return multi_loads(properties_response)

        async def request_events(ace_session):
            protocol = await Context.create_client_context()
            client = CoAPClient(client_id = CLIENT_ID,
                                client_secret = CLIENT_SECRET,
                                protocol = protocol
                                )
            events_response = await client.access_resource(session = ace_session,
                                                        rs_url = self.url,
                                                        endpoint = '/events')
            return multi_loads(events_response)


        thing_state = asyncio.new_event_loop().run_until_complete(request_thing(self.ace_session))
        properties_state = asyncio.new_event_loop().run_until_complete(request_properties(self.ace_session))
        events_state = asyncio.new_event_loop().run_until_complete(request_events(self.ace_session))


        self.name = thing_state['name']
        self.description = thing_state['description']
        self.properties_update(thing_state, properties_state)
        self.actions.update(thing_state['actions'])
        self.events_update(events_state)



    def request_acess_token(self):

        async def request():
            protocol = await Context.create_client_context()

            client = CoAPClient(client_id = CLIENT_ID,
                                client_secret = CLIENT_SECRET,
                                protocol = protocol
                                )

            ace_session = await client.request_access_token(as_url = AS_URL,
                                                            audience = AUDIENCE,
                                                            scopes = SCOPES
                                                            )
            return ace_session

        return asyncio.new_event_loop().run_until_complete(request())




    def upload_access_token(self):

        async def request(ace_session):
            protocol = await Context.create_client_context()

            client = CoAPClient(client_id = CLIENT_ID,
                                client_secret = CLIENT_SECRET,
                                protocol = protocol
                                )

            await client.upload_access_token(session = ace_session,
                                             rs_url = self.url,
                                             endpoint = '/authz-info')

        asyncio.new_event_loop().run_until_complete(request(self.ace_session))
