from gateway_addon import Property
# imports parameters.py
from pkg.parameters import *


class AceProperty(Property):


    def __init__(self, device, name, description, value):
        '''
        :param device:  The device this property belongs to.
        :param name: The name of this property.
        :param description: The description of this property, as a dictionary.
        :param value: The current value of this property.
        '''
        print(BLUE + 'AceProperty().__init__()'+ENDC)
        super().__init__(device, name, description)

        self.value = value
        self.description = description


    def update(self, value):
        """
                Update the current value, if necessary.

                light_state -- current state of the light
                """

        self.value =value
        manager_proxy = self.device.adapter.manager_proxy
        manager_proxy.send_property_changed_notification(self)


