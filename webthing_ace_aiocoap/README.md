## ACE aiocoap WebThing

A 
[_WebThing_](https://github.com/mozilla-iot/webthing-python "github.com/mozilla-iot/webthing-python")
which uses _aiocoap_ and 
[_ACE_](https://github.com/DurandA/ace/tree/master/ace/rs "github.com/DurandA/ace/tree/master/ace/rs")
.

### Files
| File | Description |
|---|---|
|`example`  | This example of launches an _ACE aiocoap WebThing_. It uses the [`VirtualRPiThing`](https://github.com/IO42630/secure_webthings/blob/master/things/virt_rpi_thing.py) Thing.|
|[`example/ace_aiocoap_client.py`](https://github.com/IO42630/secure_webthings/blob/master/webthing_ace_aiocoap/example/ace_aiocoap_client.py) | A script which makes a number of requests  to the _ACE Tornado WebThing_.|
|[`example/ace_aiocoap_server.py`](https://github.com/IO42630/secure_webthings/blob/master/webthing_ace_aiocoap/example/ace_aiocoap_server.py) | The script that launches the _ACE Tornado WebThing_.|
|[`example/authorization_server.py`](https://github.com/IO42630/secure_webthings/blob/master/webthing_ace_aiocoap/example/authorization_server.py) | The _Authorization Server_ which is used by _ACE_.|
|`webthing` | Contains the implementation of the _ACE Tornado WebThing_.|
|[`webthing/handlers.py`](https://github.com/IO42630/secure_webthings/blob/master/webthing_ace_aiocoap/webthing/handlers.py) | Contains the handlers belonging to `server.py`.|
|[`webthing/server.py`](https://github.com/IO42630/secure_webthings/blob/master/webthing_ace_aiocoap/webthing/server.py) | The implementation of the _ACE aiocoap WebThing_ .|
|`parameters.py` | Contains parameters used in either _example_ or _webthing_.|





### HowTo
+ Launch in the following order:
    1. [`authorization_server.py`](https://github.com/IO42630/secure_webthings/blob/master/webthing_ace_tornado/example/authorization_server.py).
    2. [`ace_aiocoap_server.py`](https://github.com/IO42630/secure_webthings/blob/master/webthing_ace_aiocoap/example/ace_aiocoap_server.py).
    3. [`ace_aiocoap_client.py`](https://github.com/IO42630/secure_webthings/blob/master/webthing_ace_aiocoap/example/ace_aiocoap_client.py).
+ Fields in _All Caps_ are parameters. 
Global parameters can be modified in 
[`parameters.py`](https://github.com/IO42630/secure_webthings/blob/master/webthing_ace_aiocoap/parameters.py).
In some cases it is necessary to choose which 
global parameter to choose.
This is typically done when choosing which Thing to use for the example.
These local parameters can be adjusted in the
 _LOCAL PARAMETERS_ section of the 
local file.

### ToDo
+ SingleThing is cast to MultipleThings in order to make handlers more concise.
+ Test _ActionID_ requests in `example`.
+ ActionIDHandler not functional because IDs are unpredictable.
  + Thus IDs can not be provisioned by AS.
  + ID would need to be submitted to AS.
  + AS would need to issue new Token.
+ ThingHandler returns description of Thing instead of WebSocket logic in `webthing`.
+ URI of ThingsHandler is `'/ '` instead of `'/'` `webthing`.