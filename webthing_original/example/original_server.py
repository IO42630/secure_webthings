import logging
import sys
from os import path, pardir
from webthing import SingleThing, WebThingServer


sys.path.append(path.join(path.dirname(path.abspath(__file__)), pardir, pardir))

# Comment this in when using the RPiThing .
# from things.rpi_thing import RPiThing
from things.virt_rpi_thing import VirtualRPiThing
from webthing_original.example.parameters import *





def run_server():
    thing = VirtualRPiThing()
    thing.name = 'Virtual PLAIN HTTP RPi Thing'

    server = WebThingServer(things = SingleThing(thing),
                            port = PLAIN_HTTP_RS_PORT)

    try:
        logging.info('start the server')
        logging.info('at PORT: ' + str(PLAIN_HTTP_RS_PORT))
        server.start()

    except KeyboardInterrupt:
        logging.info('stopping the server')
        server.stop()
        logging.info('done')





if __name__ == '__main__':

    logging.basicConfig(level = 10,
                        format = "%(asctime)s %(filename)s:%(lineno)s %(levelname)s %(message)s"
                        )
    run_server()
