'''
 A collection of 'dict' that describe devices.
'''
import pkg.templates.property_templates as property_templates


_onOffColorLight = {
    'name'      : 'Virtual On/Off Color Light',
    'type'      : 'onOffColorLight',
    '@context'  : 'https://iot.mozilla.org/schemas',
    '@type'     : ['OnOffSwitch', 'Light', 'ColorControl'],
    'properties': [
        property_templates.on,
        property_templates.color,
        property_templates.authz_info,
        property_templates.well_known_edhoc,
        ],
    'actions'   : [],
    'events'    : [],
    }

_onOffColorTemperatureLight = {
    'name'      : 'Virtual On/Off Color Temperature Light',
    'type'      : 'onOffColorLight',
    '@context'  : 'https://iot.mozilla.org/schemas',
    '@type'     : ['OnOffSwitch', 'Light', 'ColorControl'],
    'properties': [
        property_templates.on,
        property_templates.colorTemperature,
        property_templates.authz_info,
        property_templates.well_known_edhoc,
        ],
    'actions'   : [],
    'events'    : [],
    }

_dimmableColorLight = {
    'name'      : 'Virtual Dimmable Color Light',
    'type'      : 'dimmableColorLight',
    '@context'  : 'https://iot.mozilla.org/schemas',
    '@type'     : ['OnOffSwitch', 'Light', 'ColorControl'],
    'properties': [
        property_templates.on,
        property_templates.color,
        property_templates.brightness,
        property_templates.authz_info,
        property_templates.well_known_edhoc,
        ],
    'actions'   : [],
    'events'    : [],
    }

_binarySensor = {
    'name'      : 'Virtual Binary Sensor',
    'type'      : 'binarySensor',
    '@context'  : 'https://iot.mozilla.org/schemas',
    '@type'     : ['BinarySensor'],
    'properties': [
        property_templates.bool,
        property_templates.authz_info,
        property_templates.well_known_edhoc,
        ],
    'actions'   : [],
    'events'    : [],
    }

DEVICE_TEMPLATES = [
    _onOffColorLight,
    _onOffColorTemperatureLight,
    _dimmableColorLight,
    _binarySensor
    ]
