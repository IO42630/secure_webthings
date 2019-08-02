import socket


from gateway_addon import Adapter, SetPinError

from pkg.addon_manager_proxy import AceAddonManagerProxy
from pkg.device import *

from pkg.parameters import *

from zeroconf import ServiceBrowser, Zeroconf
import logging





_TIMEOUT = 3



# For now ignore 'pairing' checks , ignore 'pin' features.
class AceAdapter(Adapter):

    def __init__(self, _id, package_name, verbose = False):
        """
        Initialize the object.

        As part of initialization, a connection is established between the
        adapter and the Gateway via nanomsg IPC.

        _id -- the adapter's individual ID
        package_name -- the adapter's package name
        verbose -- whether or not to enable verbose logging
        """
        self.verbose = verbose
        if self.verbose:
            print(BLUE + 'AceAdapter().__init__()' + ENDC)

        # NOTE: error if absent
        self.name = self.__class__.__name__

        self.id = _id
        self.package_name = package_name
        self.devices = {}
        self.actions = {}
        self.knownUrls = {}

        # We assume that the adapter is ready right away. If, for some reason,
        # a particular adapter needs some time, then it should set ready to
        # False in it's constructor.
        self.ready = True

        self.manager_proxy = AceAddonManagerProxy(self.id, verbose = verbose)
        # ting-url-adapter.js : 406
        self.manager_proxy.add_adapter(self)








    def proxy_running(self):
        """Return boolean indicating whether or not the proxy is running."""
        return self.manager_proxy.running

    def close_proxy(self):
        """Close the manager proxy."""
        self.manager_proxy.close()

    def send_error(self, message):
        """
        Send an error notification.

        message -- error message
        """
        self.manager_proxy.send_error(message)

    def dump(self):
        """Dump the state of the adapter to the log."""
        print('Adapter:', self.name, '- dump() not implemented')

    def get_id(self):
        """
        Get the ID of the adapter.

        Returns the ID as a string.
        """
        return self.id

    def get_package_name(self):
        """
        Get the package name of the adapter.

        Returns the package name as a string.
        """
        return self.package_name

    def get_device(self, device_id):
        """
        Get the device with the given ID.

        device_id -- ID of device to retrieve

        Returns a Device object, if found, else None.
        """
        return self.devices.get(device_id, None)

    def get_devices(self):
        """
        Get all the devices managed by this adapter.

        Returns a dictionary of device_id -> Device.
        """
        return self.devices

    def get_name(self):
        """
        Get the name of this adapter.

        Returns the name as a string.
        """
        return self.name

    def is_ready(self):
        """
        Get the ready state of this adapter.

        Returns the ready state as a boolean.
        """
        return self.ready

    def as_dict(self):
        """
        Get the adapter state as a dictionary.

        Returns the state as a dictionary.
        """
        return {
            'id'   : self.id,
            'name' : self.name,
            'ready': self.ready,
            }

    def handle_device_added(self, device):
        """
        Notify the Gateway that a new device is being managed by this adapter.

        device -- Device object
        """
        if self.verbose:
            print(BLUE + 'AceAdapter().handle_device_added()' + ENDC)
        self.devices[device.id] = device
        self.manager_proxy.handle_device_added(device)

    def handle_device_removed(self, device):
        """
        Notify the Gateway that a device has been removed.

        device -- Device object
        """
        if self.verbose:
            print(BLUE + 'AceAdapter().handle_device_removed()' + ENDC)
        if device.id in self.devices:
            del self.devices[device.id]

        self.manager_proxy.handle_device_removed(device)



    def start_pairing(self, timeout):
        # TODO this is where ACE-WebThingServer will be added.
        # addon-manager-proxy.js:153
        print('Adapter:', self.name, 'id', self.id, 'pairing started')
        self.pairing = True

        discovered_devices: dict = {}




        class WebThingListener:

            def __init__(self):
                self.prefix = ''

            def add_service(self, zeroconf, type, name):
                """ Called automatically by ServiceBrowser. """
                _info = zeroconf.get_service_info(type, name)
                _name: str = _info.name.split('.')[0]
                _address: str = self.prefix + socket.inet_ntoa(_info.address) + ':' + str(_info.port)
                discovered_devices[_name] = _address
                print('Device ' + _name + ' discovered at ' + _address)


            def remove_service(self, zeroconf, type, name):
                """ Called automatically by ServiceBrowser. """
                pass




        class HTTPWebThingListener(WebThingListener):
            def __init__(self):
                super().__init__()
                self.prefix = 'http://'




        class CoAPWebThingListener(WebThingListener):
            def __init__(self):
                super().__init__()
                self.prefix = 'coap://'




        self.zeroconf = Zeroconf()
        self.tcp_browser = ServiceBrowser(self.zeroconf, "_webthing._tcp.local.", HTTPWebThingListener())
        self.udp_browser = ServiceBrowser(self.zeroconf, "_webthing._udp.local.", CoAPWebThingListener())
        time.sleep(0.5)

        for dev_name in discovered_devices:
            if not self.pairing:
                break

            if dev_name not in self.devices:
                if 'PLAIN' in dev_name:
                    device = URLDevice(adapter = self,
                                       _id = dev_name,
                                       url = discovered_devices[dev_name])
                    self.handle_device_added(device)

                elif 'ACE' in dev_name and 'HTTP' in dev_name:
                    device = AceURLDevice(adapter = self,
                                          _id = dev_name,
                                          url = discovered_devices[dev_name])
                    self.handle_device_added(device)

                elif 'ACE' in dev_name and 'CoAP' in dev_name:
                    device = CoapAceURLDevice(adapter = self,
                                              _id = dev_name,
                                              url = discovered_devices[dev_name])
                    self.handle_device_added(device)





    def cancel_pairing(self):
        self.pairing = False
        print('Adapter:', self.name, 'id', self.id, 'pairing cancelled')



    def remove_thing(self, device_id):
        """
        Unpair a device with the adapter.

        device_id -- ID of device to unpair
        """
        device = self.get_device(device_id)
        logging.info(
                ':  Stopping polling_thread(' + device.polling_thread._name + ') for Device:  ' + device.name + '.')

        device.stop_event.set()
        device.polling_thread.join()
        # device.polling_thread.stop()
        if device:
            print('Adapter:', self.name, 'id', self.id,
                  'remove_thing(' + device.id + ')')

            self.handle_device_removed(device)

    def cancel_remove_thing(self, device_id):
        """
        Cancel unpairing of a device.

        device_id -- ID of device to cancel unpairing with
        """
        device = self.get_device(device_id)
        if device:
            print('Adapter:', self.name, 'id', self.id,
                  'cancel_remove_thing(' + device.id + ')')

    def unload(self):
        """Perform any necessary cleanup before adapter is shut down."""
        print('Adapter:', self.name, 'unloaded')

    def set_pin(self, device_id, pin):
        """
        Set the PIN for the given device.

        device_id -- ID of device
        pin -- PIN to set
        """
        device = self.get_device(device_id)
        if device:
            print('Adapter:', self.name, 'id', self.id,
                  'set_pin(' + device.id + ', ' + pin + ')')
        else:
            raise SetPinError('Device not found')
