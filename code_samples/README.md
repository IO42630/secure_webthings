# README ./examples
## Overview of this Document
+ Package Contents
+ How To Run
+ Some Notes
+ Grants
+ AS Example (executable)

## Package Contents
+ `pure_webthings` original example by Mozilla.
  + `pure_wt_cl.py` requests `GET /properties/brightness`.
  + `pure_wt_rs.py` example RS from `https://iot.mozilla.org/things/`.
+ `things` contains Things to load into WebThingServer.
  + `virtual_temperature.py`
+ `ace_as_ex.py` starts Authorization Server for all examples.
+ `ace_coap_cl_ex.py` starts Client for ACE-CoAP example.
+ `ace_coap_rs_ex.py` starts Resource Server for ACE-CoAP example.
+ `ace_http_cl_ex.py` starts ACE HTTP Client.
  + To be revised.
+ `ace_http_rs_ex.py` starts ACE HTTP Resource Server.
  + To be revised.
+ `dummy_coap_cl.py` sends CoAP requests without context. 
+ `dummy_http_cl.py` sends HTTP requests without context.  
+ `empty_file.py` scratchpad.  
+ `global_parameters.py` modify `parameters` for all examples here.
+ `wt_aiocoap_cl_ex` starts Client for aio-webthings CoAP example.
  + Structurally identical to `ace_coap_cl_ex.py`.
+ `wt_aiocoap_rs_ex` starts aio-webthings CoAP Resource Server.
+ `wt_aiohttp_rs_ex` starts aio-webthings HTTP Resource Server.
  + To be completed.

## How To Run
1. Start AS (always `ace_as_ex.py`).
1. Start RS (`CoAP` or `HTTP`, ACE or aio-webthings).
1. Start CL (`CoAP` or `HTTP`, always ACE).

## Some Notes
With this CoAP server there are a few central variables.
+ `audience` indicates a device of interest.
In ACE this would be a Sensor. 
In WT-CoAP this is a Webthing.
Here it is equivalent to the `name` of the `things` object . 
`audience` is NOT the `WebThingServer`.
  + Example: `virtual_temperature_thing`
+ The attributes of an `audience` have an `uri`.
Depending on wether the protocol is coap or http it is represented by either 
a tuple or a string.
  + http: `/properties/temperature`
  + coap: `('properties','temperature')`
+ The `scope` is an allowed call to the device. It's syntax matches the following pattern:
  + `GET /properties/temperature`
  + `POST /properties/temperature`
  
## Grants
In the original ACE Grants had the following syntax:
 + `Grant(audience="tempSensor0", scopes=["read_temperature",])`  

Here the following pattern is used:
  + `Grant(audience=thing_name, scopes = ['GET /properties/temperature',]`  
  
 This Grant exists in two independent, and not necessarily identical, instances. 
 1. Stored in the WebThing Server, 
 which generates Grants from the description of the Things it hosts.
    1. This instance considers the properties of Things. For example the 'readOnly' metadata entry.
 1. ACE Authorization Server defines an audience, grants tuple
 when pre-registering clients.
 
 ## AS example (executable)
    
ABOUT: This is a makeshift overview of the calls issued in this file.
- provision private key
- initialize web app (AS)
  + define loop (scheduler)
  + get Application(loop) which contains .router
- define AuthorizationServer()
   + init: self. ClientRegistry() ,  KeyRegistry(), TokenRegistry(), Dict[str, ResourceServer]
     + add /token and /introspect to self.router
- pre-register RS, CL
   + AuthorizationServer.register_resource_server()
   + AuthorizationServer.register_client()
- run web app (AS)