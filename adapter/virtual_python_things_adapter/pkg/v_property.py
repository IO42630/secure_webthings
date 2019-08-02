from gateway_addon import Property


class VirtualProperty(Property):


    def __init__(self, device, name, description, value):
        '''
        :param device:  The device this property belongs to.
        :param name: The name of this property.
        :param description: The description of this property, as a dictionary.
        :param value: The current value of this property.
        '''
        super().__init__(device, name, description)

        if 'readOnly' in self.description and not self.description['readOnly']:
            self.set_value(value)


