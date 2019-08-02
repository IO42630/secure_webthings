# Create implicit path.
import sys
from os import path , pardir
sys.path.append(path.join(path.dirname(path.abspath(__file__)), pardir, pardir))

# External imports.
import logging
from webthing import SingleThing

# Internal imports.
from webthing_ace_aiocoap.webthing.server import CoapWebThingServer
from webthing_ace_aiocoap.parameters import *
from things.virt_rpi_thing import VirtualRPiThing

# LOCAL PARAMETERS
AS_URL = PC_AS_URL
RS_URL = PC_ACE_COAP_RS_URL
RS_PORT = ACE_COAP_RS_PORT
HOST = COAP_HOST

def run_server():
    """
    If adding more than one Thing use MultipleThings() and supply a `name`.
    In the case of a SingleThing the SingleThing's `name` will be set as `name`.
    To change the Thing hosted by this Server edit `parameters.py`.
    """
    thing = VirtualRPiThing()
    thing.name = 'Virtual ACE CoAP RPi Thing'

    server = CoapWebThingServer(things = SingleThing(thing),
                                port = RS_PORT,
                                hostname = HOST)
    try:
        logging.info('Starting a CoapWebThingServer at [ ' + RS_URL + ' ].')
        server.start()
    except KeyboardInterrupt:
        logging.info('Stopping the server.')
        server.stop()
        logging.info('Done.')
    except Exception as e:
        print(e)


if __name__ == '__main__':
    logging.basicConfig(
            level = 10,
            format = "%(asctime)s %(filename)s:%(lineno)s %(levelname)s %(message)s"
            )
    run_server()
