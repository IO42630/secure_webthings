# Create implicit path.
import sys
from os import path, pardir
sys.path.append(path.join(path.dirname(path.abspath(__file__)), pardir, pardir))

# External imports.
import asyncio
import json
from cbor2 import dumps
from ace.client.http import HTTPClient

# Internal imports.
from webthing_ace_tornado.parameters import *

# LOCAL PARAMETERS
AS_URL = PC_AS_URL
RS_URL = PC_ACE_HTTP_RS_URL

# initialized by initialize()
client = None
ace_session = None



async def initialize():
    client = HTTPClient(client_id = CLIENT_ID,
                        client_secret = CLIENT_SECRET
                        )

    # Request access token
    ace_session = await client.request_access_token(as_url = PC_AS_URL,
                                                    audience = AUDIENCE,
                                                    scopes = SCOPES
                                                    )

    # Upload `token` to RS.
    # Returns `status=201` and `body=None`.
    # For more details, see `ace_custom.client.http_client.HTTPClient()`.
    await client.upload_access_token(session = ace_session,
                                     rs_url = RS_URL,
                                     endpoint = '/authz-info')

    print(GREEN + 'POST /authz-info -> DONE.' + ENDC)

    return (client, ace_session)



async def manytests():
    # A request to / is forwarded to `ThingHandler` if `SingleThing` or `ThingsHandler` if `MultipleThings`.
    # The current example is `SingleThing`. In order to test `ThingsHandler` swap examples first.
    await make_request('GET', '/')

    # Test `properties`

    await make_request('GET', '/properties/led')

    data = dumps({b'led': False})
    await make_request('POST', '/properties/led', _data = data)

    await make_request('GET', '/properties')

    print(GREEN + 'TEST properties -> DONE.' + ENDC)

    # Test `actions`

    data = dumps({b'switch_led': {'input': {'state': True, }, }})
    await make_request('POST', '/actions/switch_led', _data = data)

    await make_request('GET', '/properties')

    await make_request('GET', '/actions/switch_led')

    data = dumps({b'switch_led': {'input': {'state': True, }, }})
    await make_request('POST', '/actions', _data = data)

    await make_request('GET', '/actions')

    print(GREEN + 'TEST actions -> DONE.' + ENDC)

    # Test `events`

    await make_request('GET', '/events')

    await make_request('GET', '/events/proximity')

    print(GREEN + 'TEST events -> DONE.' + ENDC)



async def make_request(type, endpoint, _data = None):
    response = None
    if type == 'GET':
        response = await client.access_resource(ace_session, RS_URL, endpoint)
    elif type == 'POST':
        response = await client.post_resource(ace_session, RS_URL, endpoint, _data)

    try:
        # NOTE: pretty print json.
        _msg_pretty = json.dumps(response,
                                 indent = 4)
        print(BLUE + 'Response (' + type + ' ' + endpoint + ') :' + ENDC)
        print(_msg_pretty)
    except Exception:
        print(GREEN + 'Response (' + type + ' ' + endpoint + ') :' + ENDC)
        print(str(response))



if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    client, ace_session = loop.run_until_complete(initialize())

    loop.run_until_complete(manytests())
