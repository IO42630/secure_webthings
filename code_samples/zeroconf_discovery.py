from zeroconf import ServiceBrowser, Zeroconf
import logging
import time

class MyListener:

    def remove_service(self, zeroconf, type, name):
        print("Service %s removed" % (name,))

    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        print("Service %s added, service info: %s" % (name, info))






logging.basicConfig(level = 10,
                        format = "%(asctime)s %(filename)s:%(lineno)s %(levelname)s %(message)s"
                        )
zeroconf = Zeroconf()
listener = MyListener()

try:
    logging.info('Starting ServiceBrowser.')
    ServiceBrowser(zeroconf, "_webthing._tcp.local.", listener)
    ServiceBrowser(zeroconf, "_webthing._udp.local.", listener)

    while True:
        time.sleep(10)


except KeyboardInterrupt:
    logging.info('Stopping ServiceBrowser . . .')
    zeroconf.close()
    logging.info('done.')
except Exception as e:
    print(e)