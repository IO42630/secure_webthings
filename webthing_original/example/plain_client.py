import asyncio
import aiohttp
import json

from webthing_original.example.parameters import *


target_url = PLAIN_HTTP_RS_URL


# Comment this in when using an address that is not `localhost` .
# target_url = 'http://192.168.43.17:8081'


async def main():
    client_session = aiohttp.ClientSession()

    await make_request(client_session, 'GET', '/')

    await make_request(client_session, 'GET', '/properties')

    await make_request(client_session, 'GET', '/events')

    await make_request(client_session, 'GET', '/events/proximity')

    data = json.dumps({'led': False})
    await make_request(client_session, 'PUT', '/properties/led', _data = data)

    data = json.dumps({'pressure': 90})
    await make_request(client_session, 'PUT', '/properties/pressure', _data = data)

    data = json.dumps({'switch_led': {'input': {'state': True, }, }})
    await make_request(client_session, 'POST', '/actions/switch_led', _data = data)

    await make_request(client_session, 'GET', '/properties')

    data = json.dumps({'switch_led': {'input': {'state': False, }, }})
    await make_request(client_session, 'POST', '/actions/switch_led', _data = data)

    await make_request(client_session, 'GET', '/properties')

    await client_session.close()





async def make_request(session, method, endpoint, _data = None):
    response = None
    if method == 'GET':
        response = await session.get(target_url + endpoint)
    elif method == 'POST':
        response = await session.post(target_url + endpoint, data = _data)
    elif method == 'PUT':
        response = await session.put(target_url + endpoint, data = _data)

    if response.status < 200 or response.status >= 300:
        print(RED + 'ERROR: '
              + str(response.status) + ' ' + response.reason + ' ('
              + method + ' ' + endpoint + ') ' + ENDC)
        return

    stream_reader = response.content
    byte_content = await stream_reader.read(-1)
    dict_content = json.loads(byte_content)

    try:
        # NOTE: pretty print json.
        _msg_pretty = json.dumps(dict_content,
                                 indent = 4)
        print(BLUE + 'Response (' + method + ' ' + endpoint + ') :' + ENDC)
        print(ENDC + _msg_pretty)
    except Exception:
        print(GREEN + 'Response (' + method + ' ' + endpoint + ') :' + ENDC)
        print(str(response))





if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
