# virtual-python-things adapter for Mozilla IoT Gateway.

import functools
import logging
from os import path

import sys
sys.path.append('/usr/local/lib/python3.6/dist-packages')
# https://github.com/mozilla-iot/gateway-addon-python
import gateway_addon
import signal

import time


# mark parent of pkg as sources root, and append pkg to sys.path, them import starting with pkg. .
sys.path.append(path.join(path.dirname(path.abspath(__file__)), 'lib'))
from pkg.adapter import AceAdapter


_API_VERSION = {
    'min': 1,
    'max': 2,
    }

print('main.py started')

_ADAPTER = None

print = functools.partial(print, flush = True)


def cleanup(signum, frame):
    """Clean up any resources before exiting."""
    if _ADAPTER is not None:
        _ADAPTER.close_proxy()

    sys.exit(0)


if __name__ == '__main__':
    logging.basicConfig(
            level = 10,
            format = "%(asctime)s %(filename)s:%(lineno)s %(levelname)s %(message)s"
            )

    if gateway_addon.API_VERSION < _API_VERSION['min'] or \
            gateway_addon.API_VERSION > _API_VERSION['max']:
        print('Unsupported API version: ', gateway_addon.API_VERSION)
        sys.exit(0)

    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    # STEP 1 of current ERROR
    _ADAPTER = AceAdapter(verbose = True,
                          _id = 'ace_adapter',
                          package_name = 'ace_adapter', )

    # Wait until the proxy stops running, indicating that the gateway shut us
    # down.
    while _ADAPTER.proxy_running():
        time.sleep(2)
