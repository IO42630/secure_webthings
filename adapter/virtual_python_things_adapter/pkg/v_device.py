from gateway_addon import Device
from pkg.v_property import VirtualProperty


class VirtualDevice(Device):

    def __init__(self,
                 adapter,
                 _id,
                 device_template: dict):
        """
        py-syntax: dict[string:key] refers to the value of dict at string:key
        value of key 'properties' is an list of dict
        value of key 'actions' is todo
        value of key 'events' is todo
          + adapter:
          + _id: globally unique identifier.
          + device_template :
        """
        super().__init__(adapter, _id)

        # Copy all values from `template`.
        self.name = device_template['name']
        self.type = device_template['type']
        self._context = device_template['@context']
        self._type = device_template['@type']

        for property_template in device_template['properties']:
            property = VirtualProperty(self,
                                       property_template['name'],
                                       property_template['description'],
                                       property_template['value'])

            # self.properties is dict { 'name' : object }
            self.properties[property.name] = property

        _ = 'break'
        # for template_action in template['actions']:
        #    self.add_action(template_action.name, template_action.metadata)

        # for template_event in template['events']:
        #    self.add_event(template_event.name, template_event.metadata)

        # not needed because done in adapter.start.pairing(), keep here just in case commenting this out causes a bug.
        #self.adapter.handle_device_added(self)
