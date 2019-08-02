from gateway_addon import Adapter
from pkg.templates.thing_templates import DEVICE_TEMPLATES
from pkg.v_device import VirtualDevice


_TIMEOUT = 3


# For now ignore 'pairing' checks , ignore 'pin' features.
class VirtualAdapter(Adapter):

    def __init__(self, verbose):
        self.name = self.__class__.__name__
        Adapter.__init__(self,
                         'virtual-python-things-adapter',
                         'virtual-python-things-adapter',
                         verbose=verbose)
        self.pairing = False
        self.start_pairing(_TIMEOUT)



    def start_pairing(self, timeout):

        self.pairing = True

        for device_template in DEVICE_TEMPLATES:

            if not self.pairing:
                break

            _id='virtual_python_things_' + device_template['type']

            if _id not in self.devices:
                virtual_device = VirtualDevice(self, _id, device_template)
                self.handle_device_added(virtual_device)





    def cancel_pairing(self):
        self.pairing = False