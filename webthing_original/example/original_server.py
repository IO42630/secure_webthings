import logging

from webthing import SingleThing, WebThingServer

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
        logging.info('Starting the server.')
        logging.info('at PORT: ' + str(PLAIN_HTTP_RS_PORT))
        server.start()

    except KeyboardInterrupt:
        logging.info('Stopping the server.')
        server.stop()
        logging.info('Done.')


if __name__ == '__main__':
    logging.basicConfig(level = 10,
                        format = "%(asctime)s %(filename)s:%(lineno)s %(levelname)s %(message)s"
                        )
    run_server()
