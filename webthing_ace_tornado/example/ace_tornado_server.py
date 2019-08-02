# Create implicit path.
import sys
from os import path, pardir
sys.path.append(path.join(path.dirname(path.abspath(__file__)), pardir, pardir))

# External imports.
import logging
from webthing import SingleThing

# Internal imports.
from webthing_ace_tornado.webthing.server import AceWebThingServer
from webthing_ace_tornado.parameters import *
from things.virt_rpi_thing import VirtualRPiThing



def run_server():
    """
    If adding more than one Thing use MultipleThings() and supply a `name`.
    In the case of a SingleThing the SingleThing's `name` will be set as `name`.
    To change the Thing hosted by this Server edit `parameters.py`.
    """
    thing = VirtualRPiThing()
    thing.name = 'Virtual ACE HTTP RPi Thing'

    server = AceWebThingServer(things = SingleThing(thing),
                               port = ACE_HTTP_RS_PORT)
    try:
        logging.info('Starting the server at PORT: ' + str(ACE_HTTP_RS_PORT))
        server.start()
    except KeyboardInterrupt:
        logging.info('Stopping the server . . .')
        server.stop()
        logging.info('done.')
    except Exception as e:
        print(e)


if __name__ == '__main__':
    logging.basicConfig(level = 10,
                        format = "%(asctime)s %(filename)s:%(lineno)s %(levelname)s %(message)s"
                        )
    run_server()
