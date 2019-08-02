bool = {
        'name'      : 'on',
        'value'     : False,
        'description'  : {
            'label'     : 'On/Off',
            'type'      : 'boolean',
            '@type'     : 'BooleanProperty',
            'readOnly'  : True,
        },
    }


on = {
        'name'      : 'on',
        'value'     : False,
        'description'  : {
            'label'     : 'On/Off',
            'type'      : 'boolean',
            '@type'     : 'OnOffProperty',
        },
    }


color = {
        'name'      : 'color',
        'value'     : '#ffffff',
        'description'  : {
            'label'     : 'Color',
            'type'      : 'string',
            '@type'     : 'ColorProperty',
        },
    }


colorTemperature = {
        'name'      : 'colorTemperature',
        'value'     : 2500,
        'description'  : {
            'label'     : 'Color Temperature',
            'type'      : 'number',
            '@type'     : 'ColorTemperatureProperty',
            'unit'      : 'kelvin',
            'min'       : 2500,
            'max'       : 9000,
        },
    }


brightness = {
        'name'      : 'level',
        'value'     : 0,
        'description'  : {
            'label'     : 'Brightness',
            'type'      : 'number',
            '@type'     : 'BrightnessProperty',
            'unit'      : 'percent',
            'min'       : 0,
            'max'       : 100,
        },
    }