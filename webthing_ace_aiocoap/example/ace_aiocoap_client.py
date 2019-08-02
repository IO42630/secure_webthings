# Create implicit path.
import sys
from os import path, pardir
sys.path.append(path.join(path.dirname(path.abspath(__file__)), pardir, pardir))

# External imports.
import asyncio
import json

from cbor2 import dumps
from aiocoap import Context


from ace.client.coap import CoAPClient

# Internal imports.
from webthing_ace_aiocoap.parameters import *

# LOCAL PARAMETERS
AS_URL = PC_AS_URL
RS_URL = PC_ACE_COAP_RS_URL

# initialized by initialize()
client = None
ace_session = None



async def initialize():
    protocol = await Context.create_client_context()
    client = CoAPClient(client_id = CLIENT_ID,
                        client_secret = CLIENT_SECRET,
                        protocol = protocol)
    # Request access token
    ace_session = await client.request_access_token(as_url = AS_URL,
                                                                audience = AUDIENCE,
                                                                scopes = SCOPES
                                                                )
    # Upload token to RS
    await client.upload_access_token(session = ace_session,
                                     rs_url = RS_URL,
                                     endpoint = '/authz-info')

    print(GREEN + 'POST /authz-info -> DONE.' + ENDC)

    return (client, ace_session)



async def manytests():
    # Test `root`
    await make_request('GET', '/ ')

    # Test `properties`
    await make_request('GET', '/properties/led')

    await make_request('POST', '/properties/led', _data = dumps({'led': True}))

    await make_request('GET', '/properties')

    print(GREEN + 'TEST properties -> DONE.' + ENDC)

    # Test `actions`

    data = dumps({'switch_led': {'input': {'state': True, }}})
    await make_request('POST', '/actions/switch_led', _data = data)

    await make_request('GET', '/actions/switch_led')

    await make_request('POST', '/actions', _data = data)

    await make_request('GET', '/actions')

    print(GREEN + 'TEST events -> DONE.' + ENDC)

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



if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    client, ace_session = loop.run_until_complete(initialize())

    loop.run_until_complete(manytests())
