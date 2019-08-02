import asyncio
import ssl

import aiohttp
import json

HEADER = '\033[95m'
BLUE = '\033[94m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'

# target_url = PLAIN_HTTP_RS_URL
target_url = 'http://localhost:4443'


async def main():
    client_session = aiohttp.ClientSession()

    #sslcontext = ssl.create_default_context(cafile = '/etc/ssl/certs/4a6481c9.0')

    await make_request(client_session, 'GET', '/things/plain_rpi_thing/properties/text')
    # await make_request(client_session, 'GET', '/properties')
    #await make_request(client_session,
    #                   'PUT', '/things/plain_rpi_thing/properties/text',
    #                   _data = json.dumps({'text': 'Client said Hi.'}),
    #                   sslcontext = False)

    # await make_request(client_session, 'PUT', '/properties/pressure', _data = json.dumps({'pressure': 90}))

    # switch_input = {'state': True, }
    # await make_request(client_session, 'POST', '/actions/switch_led',
    #                   json.dumps({'switch_led': {'input': switch_input, }}))
    # await make_request(client_session, 'GET', '/properties')
    # switch_input = {'state': False, }
    # await make_request(client_session, 'POST', '/actions/switch_led',
    #                   json.dumps({'switch_led': {'input': switch_input, }}))
    # await make_request(client_session, 'GET', '/properties')


    await client_session.close()





async def make_request(session, type, endpoint, _data = None, sslcontext = None):
    response = None
    if type == 'GET':
        response = await session.get(target_url + endpoint, ssl = sslcontext)
    elif type == 'POST':
        response = await session.post(target_url + endpoint, data = _data, ssl = sslcontext)
    elif type == 'PUT':
        response = await session.put(target_url + endpoint, data = _data, ssl = sslcontext)

    stream_reader = response.content
    byte_content = await stream_reader.read(-1)
    dict_content = json.loads(byte_content)

    try:
        # NOTE: pretty print json.
        _msg_pretty = json.dumps(dict_content,
                                 indent = 4)
        print(BLUE + 'Response (' + type + ' ' + endpoint + ') :' + ENDC)
        print(ENDC + _msg_pretty)
    except Exception:
        print(GREEN + 'Response (' + type + ' ' + endpoint + ') :' + ENDC)
        print(str(response))





if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
