# ACE URL Adapter
Add-on/Adapter for the 
[Gateway Addon](https://github.com/mozilla-iot/gateway-addon-python/tree/master/gateway_addon "https://github.com/mozilla-iot/gateway-addon-python/tree/master/gateway_addon")
. 
It allows Original WebThings, ACE Tornado WebThings and ACE aiocoap WebThings to be connected to the Gateway.


### HowTo



##### Install this Add-on
1. If you are debugging you might prefer to execute the `./ace_url_adapter/main.py` instead of following the steps below.
1.  Clone `./ace_url_adapter` to `/your_directory`.  
1.  In `main.py` change 
`sys.path.append(os.path.dirname('')`
and fix all the imports. 
2.  Create link: `ln -s /your_directory ~/.mozilla-iot/addons/`
2. To add this add-on to the WebThingsGateway copy or link the package 
(`ace_adapter`) into `~/.mozilla-iot/addons/` .
2. Now this add-on is considered installed.
2.  It can be enabled in the WebThingsGateway menu, or run 
independently via `main.py`. 

##### Test the Prototype
1. Launch the Authorization Server if you wish to test ACE Tornado WebThings or ACE aiocoap WebThings
1. Launch the desired Resource Server, such as WebThingServer `/webthing_original/example/original_server.py`.
2. Start a WebThingGateway `nmp start` . 
More details can be found in the Mozilla documentation,
or this
[Blog post](https://github.com/mozilla-iot/gateway-addon-python/tree/master/gateway_addon "https://github.com/mozilla-iot/gateway-addon-python/tree/master/gateway_addon") on how to set up a gateway.







