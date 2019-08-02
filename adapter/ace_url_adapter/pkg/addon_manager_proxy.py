"""Proxy for sending messages between the Gateway and an add-on."""
import asyncio


from gateway_addon import AddonManagerProxy
from nnpy.errors import NNError
import functools
import json
import threading
import time

from gateway_addon.ipc import IpcClient
from gateway_addon.errors import ActionError, PropertyError, SetPinError


print = functools.partial(print, flush = True)

from pkg.parameters import *


class AceAddonManagerProxy(AddonManagerProxy):
    """
    Proxy for communicating with the Gateway's AddonManager.

    This proxy interprets all of the required incoming message types that need
    to be handled by add-ons and sends back responses as appropriate.
    """


    def __init__(self, plugin_id, verbose = False):
        """
        Initialize the object.

        plugin_id -- ID of this plugin
        verbose -- whether or not to enable verbose logging
        """
        self.verbose = verbose
        if self.verbose:
            print(BLUE + 'AceAddonManagerProxy().__init__()'+ENDC)
        #
        self.adapters = {}
        self.ipc_client = IpcClient(plugin_id, verbose = verbose)
        self.plugin_id = plugin_id

        self.running = True
        self.thread = threading.Thread(target = self.recv)
        self.thread.daemon = True
        self.thread.start()


    def close(self):
        """Close the proxy."""
        self.running = False

        try:
            self.ipc_client.manager_socket.close()
            self.ipc_client.plugin_socket.close()
        except NNError:
            pass


    def send_error(self, message):
        """
        Send an error notification.

        message -- error message
        """
        self.send('pluginError', {'message': message})


    def add_adapter(self, adapter):
        """
        Send a notification that an adapter has been added.

        adapter -- the Adapter that was added
        """
        if self.verbose:
            print('AceAddonManagerProxy: add_adapter:', adapter.id)

        self.adapters[adapter.id] = adapter
        self.send('addAdapter', {
            'adapterId'  : adapter.id,
            'name'       : adapter.name,
            'packageName': adapter.package_name,
            })


    def handle_device_added(self, device):
        """
        Send a notification that a new device has been added.

        device -- the Device that was added
        """
        if self.verbose:
            print('AceAddonManagerProxy: handle_device_added:', device.id)

        device_dict = device.as_dict()
        device_dict['adapterId'] = device.adapter.id
        self.send('handleDeviceAdded', device_dict)


    def handle_device_removed(self, device):
        """
        Send a notification that a managed device was removed.

        device -- the Device that was removed
        """
        if self.verbose:
            print('AceAddonManagerProxy: handle_device_removed:', device.id)

        self.send('handleDeviceRemoved', {
            'adapterId': device.adapter.id,
            'id'       : device.id,
            })


    def send_property_changed_notification(self, prop):
        """
        Send a notification that a device property changed.

        prop -- the Property that changed
        """
        self.send('propertyChanged', {
            'adapterId': prop.device.adapter.id,
            'deviceId' : prop.device.id,
            'property' : prop.as_dict(),
            })


    def send_action_status_notification(self, action):
        """
        Send a notification that an action's status changed.

        action -- the action whose status changed
        """
        self.send('actionStatus', {
            'adapterId': action.device.adapter.id,
            'deviceId' : action.device.id,
            'action'   : action.as_dict(),
            })


    def send_event_notification(self, event):
        """
        Send a notification that an event occurred.

        event -- the event that occurred
        """
        self.send('event', {
            'adapterId': event.device.adapter.id,
            'deviceId' : event.device.id,
            'event'    : event.as_dict(),
            })


    def send_connected_notification(self, device, connected):
        """
        Send a notification that a device's connectivity state changed.

        device -- the device object
        connected -- the new connectivity state
        """
        self.send('connected', {
            'adapterId': device.adapter.id,
            'deviceId' : device.id,
            'connected': connected,
            })


    def send(self, msg_type, data):
        """
        Send a message through the IPC socket.

        msg_type -- the message type
        data -- the data to send, as a dictionary
        """
        if data is None:
            data = {}

        data['pluginId'] = self.plugin_id

        try:
            _msg = json.dumps({'messageType': msg_type,
                               'data'       : data,
                               })
            _msg_encoded = _msg.encode('utf-8')
            self.ipc_client.plugin_socket.send(_msg)
            # NOTE: pretty print json of sent.
            _msg_pretty = json.dumps({'messageType': msg_type,
                                      'data'       : data,
                                      },
                                     indent = 4)
            print(GREEN + 'AceAddonManagerProxy().send() '+ENDC + _msg_pretty)
        except NNError as e:
            print('AddonManagerProxy: Failed to send message: {}'.format(e))


    def recv(self):
        """
        Read a message from the IPC socket.
        NOTE: be careful when accessing msg, it might break this.
        """
        while self.running:

            try:
                msg = self.ipc_client.plugin_socket.recv()
            except NNError as e:
                print('AddonManagerProxy: Error receiving message from '
                      'socket: {}'.format(e))
                break


            if not msg:
                break

            try:
                msg = json.loads(msg.decode('utf-8'))


            except ValueError:
                print('AddonManagerProxy: Error parsing message as JSON')
                continue

            if 'messageType' not in msg:
                print('AddonManagerProxy: Invalid message')
                continue

            msg_type = msg['messageType']
            msg_data = msg['data']

            if True:
            #if self.verbose:
                # NOTE: pretty print json of sent.
                _msg_pretty = json.dumps({'messageType': msg_type,
                                          'data'       : msg_data,
                                          },
                                         indent = 4)
                print(BLUE + 'AceAddonManagerProxy().recv() ' + _msg_pretty+ENDC)



            if msg_type == 'unloadPlugin':
                self.send('pluginUnloaded', {})


                def close_fn(proxy):
                    # Give the message above time to be sent and received.
                    time.sleep(.5)
                    proxy.close()


                self.make_thread(close_fn, args = (self,))
                break

            if 'data' not in msg or 'adapterId' not in msg['data']:
                print('AddonManagerProxy: Adapter ID not present in message.')
                continue

            adapter_id = msg['data']['adapterId']
            if adapter_id not in self.adapters:
                print('AddonManagerProxy: Unrecognized adapter, ignoring '
                      'message.')
                continue

            adapter = self.adapters[adapter_id]

            # High-level adapter messages
            if msg_type == 'startPairing':
                self.make_thread(adapter.start_pairing,
                                 args = (msg['data']['timeout'],))
                continue

            if msg_type == 'cancelPairing':
                self.make_thread(adapter.cancel_pairing)
                continue

            if msg_type == 'unloadAdapter':
                def unload_fn(proxy, adapter):
                    adapter.unload()
                    proxy.send('adapterUnloaded',
                               {'adapterId': adapter.id})


                self.make_thread(unload_fn, args = (self, adapter))
                del self.adapters[adapter.id]
                continue

            # All messages from here on are assumed to require a valid deviceId
            if 'data' not in msg or 'deviceId' not in msg['data']:
                print('AddonManagerProxy: No deviceId present in message, '
                      'ignoring.')
                continue

            device_id = msg['data']['deviceId']
            if msg_type == 'removeThing':
                self.make_thread(adapter.remove_thing, args = (device_id,))
                continue

            if msg_type == 'cancelRemoveThing':
                self.make_thread(adapter.cancel_remove_thing,
                                 args = (device_id,))
                continue

            if msg_type == 'setProperty':
                def set_prop_fn(proxy, adapter):
                    dev = adapter.get_device(device_id)
                    if not dev:
                        return

                    prop = dev.find_property(msg['data']['propertyName'])
                    if not prop:
                        return



                    try:
                        #
                        # NOTE: both of the two following lines are needed.
                        # The first line sets the value to cache to be displayed in WebUI.
                        # The second line actually changes the property of the Thing.
                        prop.set_value(msg['data']['propertyValue'])
                        dev.set_property(msg['data']['propertyName'],
                                         msg['data']['propertyValue'])
                        if prop.fire_and_forget:
                            proxy.send_property_changed_notification(prop)
                    except PropertyError:
                        proxy.send_property_changed_notification(prop)


                self.make_thread(set_prop_fn, args = (self, adapter))
                continue

            if msg_type == 'requestAction':


                def request_action_fn(proxy, adapter):
                    action_id = msg['data']['actionId']
                    action_name = msg['data']['actionName']

                    try:
                        dev = adapter.get_device(device_id)

                        if dev:
                            action_input = None
                            if 'input' in msg['data']:
                                action_input = msg['data']['input']

                            print(FAIL+'INFO request_action from device with device_id : ' +str(device_id)+ENDC)
                            dev.request_action(action_id,
                                               action_name,
                                               action_input)

                        proxy.send('requestActionResolved', {
                            'actionName': action_name,
                            'actionId'  : action_id,
                            })
                    except ActionError:
                        proxy.send('requestActionRejected', {
                            'actionName': action_name,
                            'actionId'  : action_id,
                            })


                self.make_thread(request_action_fn, args = (self, adapter))
                continue

            if msg_type == 'removeAction':
                def remove_action_fn(proxy, adapter):
                    action_id = msg['data']['actionId']
                    action_name = msg['data']['actionName']
                    message_id = msg['data']['messageId']

                    try:
                        dev = adapter.get_device(device_id)

                        if dev:
                            dev.remove_action(action_id, action_name)

                        proxy.send('removeActionResolved', {
                            'actionName': action_name,
                            'actionId'  : action_id,
                            'messageId' : message_id,
                            })
                    except ActionError:
                        proxy.send('removeActionRejected', {
                            'actionName': action_name,
                            'actionId'  : action_id,
                            'messageId' : message_id,
                            })


                self.make_thread(remove_action_fn, args = (self, adapter))
                continue

            if msg_type == 'setPin':
                def set_pin_fn(proxy, adapter):
                    message_id = msg['data']['messageId']

                    try:
                        adapter.set_pin(device_id, msg['data']['pin'])

                        dev = adapter.get_device(device_id)
                        proxy.send('setPinResolved', {
                            'device'   : dev.as_dict(),
                            'messageId': message_id,
                            'adapterId': adapter.id,
                            })
                    except SetPinError:
                        proxy.send('setPinRejected', {
                            'deviceId' : device_id,
                            'messageId': message_id,
                            })


                self.make_thread(set_pin_fn, args = (self, adapter))
                continue


    @staticmethod
    def make_thread(target, args = ()):
        """
        Start up a thread in the background.

        target -- the target function
        args -- arguments to pass to target
        """
        t = threading.Thread(target = target, args = args)
        t.daemon = True
        t.start()
