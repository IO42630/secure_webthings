
## Things

Implementations of a [Thing](https://iot.mozilla.org/wot/)
.

### Contents:


+ `rpi_thing.py`: 
To be deployed on a matching Raspberry Pi configuration. Requires the `adafruit_bme280`
and the `adafruit_apds9960` sensors.

+ `virt_rpi_thing.py`
Is virtual, therefore requires no additional hardware in order to be launched.
Equivalent to the `real_rpi_thing.py` with constant sensory readings.

+ `virtual_temperature.py`
Adaptation of the vanilla
[`webthing-python`](https://github.com/mozilla-iot/webthing-python/tree/master/example)
 example.
