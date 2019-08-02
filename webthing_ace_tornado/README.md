## ACE Tornado WebThing

A [_WebThing_](https://github.com/mozilla-iot/webthing-python "github.com/mozilla-iot/webthing-python")
which uses _Tornado_ and [_ACE_](https://github.com/DurandA/ace/tree/master/ace/rs "github.com/DurandA/ace/tree/master/ace/rs").


### Files
| File | Description |
|---|---|
|`example`  | This example of launches an _ACE aiocoap WebThing_. It uses the [`VirtualRPiThing`](https://github.com/IO42630/secure_webthings/blob/master/things/virt_rpi_thing.py) Thing.|
|[`ace_tornado_client.py`](https://github.com/IO42630/secure_webthings/blob/master/webthing_ace_tornado/example/ace_tornado_client.py) | A script which makes a number of requests to the _ACE Tornado WebThing_.|
|[`ace_tornado_server.py`](https://github.com/IO42630/secure_webthings/blob/master/webthing_ace_tornado/example/ace_tornado_server.py) | A script that launches the _ACE Tornado WebThing_.|
|[`example/authorization_server.py`](https://github.com/IO42630/secure_webthings/blob/master/webthing_ace_aiocoap/example/authorization_server.py) | A script that launches the _Authorization Server_ which is used by _ACE_.|
|`webthing` | Contains the implementation of the _ACE Tornado WebThing_.|
|[`webthing/server.py`](https://github.com/IO42630/secure_webthings/blob/master/webthing_ace_tornado/webthing/server.py)  | Implementation of the _ACE Tornado WebThing_ .|
|`parameters.py` | Contains parameters used in either _example_ or _webthing_.|





### HowTo
+ Run in the following order:
    1. [`authorization_server.py`](https://github.com/IO42630/secure_webthings/blob/master/webthing_ace_tornado/example/authorization_server.py).
    2. [`ace_tornado_server.py`](https://github.com/IO42630/secure_webthings/blob/master/webthing_ace_tornado/example/ace_tornado_server.py). 
    3. [`ace_tornado_client.py`](https://github.com/IO42630/secure_webthings/blob/master/webthing_ace_tornado/example/ace_tornado_client.py).
+ Fields in _All Caps_ are parameters. 
Global parameters can be modified in 
[`parameters.py`](https://github.com/IO42630/secure_webthings/blob/master/webthing_ace_tornado/parameters.py).
In some cases it is necessary to choose which 
global parameter to choose.
This is typically done when choosing which Thing to use for the example.
These local parameters can be adjusted in the
 _LOCAL PARAMETERS_ section of the 
local file.

### ToDo
+ Test _ActionID_ requests in `example`.
+ The _PC_AS_URL_ parameter should be passed through _example_, 
and not imported in _server.py_.




