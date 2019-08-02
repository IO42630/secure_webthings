from webthing import (Action, Event, Property, Thing, Value)
import uuid


# Placeholder values. Are replaced with sensor data in the real_rpi_thing.py
led = True
temperature = 10
humidity = 10
pressure = 10
proximity = 0


class ProximityEvent(Event):

    def __init__(self, thing, data):
        Event.__init__(self, thing, 'proximity', data = data)



class SwitchLedAction(Action):

    def __init__(self, thing, input_):
        Action.__init__(self, uuid.uuid4().hex, thing, 'switch_led', input_ = input_)


    def perform_action(self):
        self.thing.set_property('led', self.input['state'])



class SetTextAction(Action):

    def __init__(self, thing, input_):
        Action.__init__(self, uuid.uuid4().hex, thing, 'set_text', input_ = input_)

    def perform_action(self):
        self.thing.set_property('text', self.input['text'])



class VirtualRPiThing(Thing):
    """
    A Thing which wraps a virtual Raspberry Pi.
    This is intended to allow the user to experiment with the code without a physical prototype.
    """
    def __init__(self):
        super().__init__(name = 'Virtual RPi Thing',
                         type_ = ['Virtual', 'RPi', 'Demo'],
                         description = 'A Raspberry Pi with Sensors'
                         )

        self.add_property(Property(self,
                                   'led',
                                   Value(led),
                                   metadata = {'label'      : 'LED',
                                               'type'       : 'boolean',
                                               'description': 'The state of the LED'
                                               }))
        self.add_property(Property(self,
                                   'temperature',
                                   Value(temperature),
                                   metadata = {'label'      : 'Temperature',
                                               'type'       : 'number',
                                               'readOnly'   : True,
                                               'description': 'The temperature in C.',
                                               'unit'       : 'C',
                                               }))
        self.add_property(Property(self,
                                   'humidity',
                                   Value(humidity),
                                   metadata = {
                                       'label'      : 'Humidity',
                                       'type'       : 'number',
                                       'readOnly'   : True,
                                       'description': 'The level of humidity from 0-100.',
                                       'unit'       : 'percent',
                                       }))
        self.add_property(Property(self,
                                   'pressure',
                                   Value(pressure),
                                   metadata = {'label'      : 'Pressure',
                                               'type'       : 'number',
                                               'readOnly'   : True,
                                               'description': 'The atmospheric pressure in hPa.',
                                               'unit'       : 'hPa',
                                               }))
        self.add_property(Property(self,
                                   'proximity',
                                   Value(proximity),
                                   metadata = {'label'      : 'Proximity',
                                               'type'       : 'number',
                                               'readOnly'   : True,
                                               'description': 'The relative proximity.'
                                               }))
        self.add_property(Property(self,
                                   'text',
                                   Value(initial_value = ''),
                                   metadata = {'label'      : 'Text',
                                               'type'       : 'string',
                                               'description': 'A string of text stored on the Thing.'
                                               }))

        self.add_available_action('switch_led',
                                  {
                                      'label'      : 'LED on',
                                      'description': 'Switch the LED on/off.',
                                      'input'      : {
                                          'type'      : 'object',
                                          'required'  : ['state', ],
                                          'properties': {
                                              'state': {'type': 'boolean',
                                                        },
                                              },
                                          },
                                      },
                                  cls = SwitchLedAction)
        self.add_available_action('set_text',
                                  {
                                      'label'      : 'Set text.',
                                      'description': 'Set a text.',
                                      'input'      : {
                                          'type'      : 'object',
                                          'required'  : ['text', ],
                                          'properties': {
                                              'text': {'type': 'string',
                                                       },
                                              },
                                          },
                                      },
                                  cls = SetTextAction)

        self.add_available_event('proximity',
                                 {
                                     'description': 'An object is in proximity.',
                                     'type'       : 'number',
                                     })


if __name__ == '__main__':
    v = VirtualRPiThing()
