"""Utility functions."""
import json

import cbor2


import threading

class StoppableThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self, target = None):
        super(StoppableThread, self).__init__(target= target)
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()








def multi_loads(input):
    output = None
    if isinstance(input, bytes):
        input = input.decode('utf-8')
    try:
        output = json.loads(input)
    except Exception:
        try:
            output = cbor2.loads(input)
        except Exception:
            # TODO: for some reason ACE CBOR mode input is already dict
            output = input

    return output





