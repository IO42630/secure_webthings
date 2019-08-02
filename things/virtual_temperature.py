from webthing import Action, Property, Thing, Value, Event
import uuid


class OverheatedEvent(Event) :

    def __init__(self, thing, data) :
        Event.__init__(self, thing, 'overheated', data = data)


class PostLed(Action) :

    def __init__(self, thing, input_) :
        Action.__init__(self,
                        uuid.uuid4().hex,
                        thing,
                        'post_led',
                        input_ = input_)

    def perform_action(self) :
        self.thing.set_property('led', self.input)


class VirtualTemperature(Thing) :

    def __init__(self) :
        super().__init__(name = 'virtual_temperature_thing',
                         type_ = ['Temperature', 'Virtual'],
                         description = '',
                         )

        self.add_property(Property(thing = self,
                                   name = 'temperature',
                                   value = Value(20),
                                   metadata = {
                                       'label'    : 'Temperature',
                                       'type'     : 'number',
                                       "readOnly" : True,
                                       }
                                   )
                          )

        self.add_property(Property(thing = self,
                                   name = 'led',
                                   value = Value(0),
                                   metadata = {
                                       'label' : 'LED',
                                       'type'  : 'number',
                                       },
                                   )
                          )

        self.add_available_action(
                name = 'set_led_to',
                metadata = {
                    'input' : {
                        'properties' : {
                            'led' : {
                                'type' : 'number',
                                },
                            },
                        },
                    },
                cls = PostLed
                )

        self.add_available_event(
                'overheated',
                {
                    'description' : 'The lamp has exceeded its safe operating temperature',
                    'type'        : 'number',
                    'unit'        : 'celsius',
                    })
