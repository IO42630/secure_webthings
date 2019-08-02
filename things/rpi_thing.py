""" The Real Raspberry Pi Thing. To be run on the Raspberry Pi."""
import threading

from webthing import (Action, Event, Property, Thing, Value)
import uuid

import board
import busio
import adafruit_bme280
import adafruit_apds9960.apds9960

import RPi.GPIO as GPIO
import time


# Interval between poll request to the sensors of the RPi.
_POLL_INTERVAL = 10




class ProximityEvent(Event):

    def __init__(self, thing, data):
        Event.__init__(self, thing, 'proximity', data = data)
        if self.data is True:
            GPIO.output(24, GPIO.HIGH)
            thing.properties['led'].value.last_value = True
        elif self.data is False:
            GPIO.output(24, GPIO.LOW)
            thing.properties['led'].value.last_value = False



class SwitchLedAction(Action):

    def __init__(self, thing, input_):
        Action.__init__(self, uuid.uuid4().hex, thing, 'switch_led', input_ = input_)


    def perform_action(self):
        if self.input['state'] is True:
            GPIO.output(24, GPIO.HIGH)
        elif self.input['state'] is False:
            GPIO.output(24, GPIO.LOW)
        else:
            raise Exception

        self.thing.set_property('led', self.input['state'])


class SetTextAction(Action):

    def __init__(self, thing, input_):
        Action.__init__(self, uuid.uuid4().hex, thing, 'set_text', input_ = input_)

    def perform_action(self):
        self.thing.set_property('text', self.input['text'])



class RPiThing(Thing):
    """
    Forms the Thing which wraps the Raspberry Pi.
    """
    def __init__(self):

        # Prepare GPIO for LED manipulation.
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(24, GPIO.OUT)

        # Prepare I2C sensors.
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.bme280 = adafruit_bme280.Adafruit_BME280_I2C(self.i2c)
        self.apds9960 = adafruit_apds9960.apds9960.APDS9960(self.i2c)
        self.apds9960.enable_proximity = True
        self.apds9960.enable_color = True

        super().__init__(name = 'RPi Thing',
                         type_ = ['RPi', 'Demo'],
                         description = 'A Raspberry Pi with Sensors'
                         )

        self.add_property(Property(self,
                                   'led',
                                   Value(False),
                                   metadata = {'label'      : 'LED',
                                               'type'       : 'boolean',
                                               'description': 'The state of the LED'
                                               }))
        self.add_property(Property(self,
                                   'temperature',
                                   Value(initial_value = self.bme280.temperature),
                                   metadata = {'label'      : 'Temperature',
                                               'type'       : 'number',
                                               'readOnly'   : True,
                                               'description': 'The temperature in C.',
                                               'unit'       : 'C',
                                               }))
        self.add_property(Property(self,
                                   'humidity',
                                   Value(initial_value = self.bme280.humidity),
                                   metadata = {
                                       'label'      : 'Humidity',
                                       'type'       : 'number',
                                       'readOnly'   : True,
                                       'description': 'The level of humidity from 0-100.',
                                       'unit'       : 'percent',
                                       }))
        self.add_property(Property(self,
                                   'pressure',
                                   Value(initial_value = self.bme280.pressure),
                                   metadata = {'label'      : 'Pressure',
                                               'type'       : 'number',
                                               'readOnly'   : True,
                                               'description': 'The atmospheric pressure in hPa.',
                                               'unit'       : 'hPa',
                                               }))
        self.add_property(Property(self,
                                   'proximity',
                                   Value(initial_value = self.apds9960.proximity()),
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

        # Start thread for polling.
        t = threading.Thread(target = self.poll)
        t.daemon = True
        t.start()



    def poll(self):
        while True:
            time.sleep(_POLL_INTERVAL)

            if self.apds9960.proximity() == 0:
                GPIO.output(24, GPIO.LOW)
                self.properties['led'].value.last_value = False
            else:
                self.add_event(ProximityEvent(self, True))

            try:
                self.properties['temperature'].value.last_value = self.bme280.temperature
                self.properties['humidity'].value.last_value = self.bme280.humidity
                self.properties['pressure'].value.last_value = self.bme280.pressure
                self.properties['proximity'].value.last_value = self.apds9960.proximity()
            except Exception as e:
                print('polling failed:  ' + str(e))
                continue



    def set_property(self, property_name, value):
        """
        Overrides the original `set_property` in order to manipulate the `last_value` and the LED as required.
        """
        prop = self.find_property(property_name)
        if not prop:
            return

        if property_name == 'led':
            if value:
                GPIO.output(24, GPIO.HIGH)
            else:
                GPIO.output(24, GPIO.LOW)

        self.properties[property_name].value.last_value = value
        prop.set_value(value)



if __name__ == '__main__':
    r = RPiThing()
