import logging
import asyncio

from aiocoap import *

from examples.global_parameters import GlobalParameters




param = GlobalParameters()
logging.basicConfig(level=logging.INFO)

async def main():
    """Perform a single PUT request to localhost on the default port, URI
    "/other/block". The request is sent 2 seconds after initialization.

    The payload is bigger than 1kB, and thus sent as several blocks."""

# /usr/local/lib/python3.6/dist-packages/aiocoap/numbers/codes.py
    GET = 1
    POST = 2
    PUT = 3

    context = await Context.create_client_context()

    await asyncio.sleep(2)

    payload = b"The quick brown fox jumps over the lazy dog.\n" * 30
    '''
    request = Message(code=GET, 
                      payload=payload, 
                      uri="coap://"+param.RS_HOST+":"+str(param.RS_PORT)+ "/hello")
    '''
    request = Message(code = GET,
                      payload = payload,
                      uri = "coap://localhost:8094/hello")

    response = await context.request(request).response

    print('Result: %s\n%r'%(response.code, response.payload))

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())