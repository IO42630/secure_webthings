from webthing import SingleThing, WebThingServer


from examples.global_parameters import GlobalParameters
from things.virtual_temperature import VirtualTemperature
import logging



param = GlobalParameters()

logging.basicConfig(level = 10,
                    format = "%(asctime)s %(filename)s:%(lineno)s %(levelname)s %(message)s")

virtual_temperature_container = SingleThing(VirtualTemperature())

server = WebThingServer(
        things = virtual_temperature_container,
        port = param.RS_PORT,
        hostname = param.RS_HOST)

try :
    logging.info('Starting the server.')
    server.start()
except KeyboardInterrupt :
    logging.info('Stopping the server.')
    server.stop()
    logging.info('Done.')
