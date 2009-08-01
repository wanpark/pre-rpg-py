# -*- coding:utf-8 -*-

"rpg.event - handle ui events"

import pygame.event
from pygame.locals import *

listeners = {}

down_keys = set()
up_keys = set()
pressed_keys = set()

def add_listener(type, listener):
    listeners.setdefault(type, set()).add(listener)

def remove_listener(type, listener):
    if type not in listeners: return
    safe_remove(listeners[type], listener)
    if len(listeners[type]) == 0:
        del listeners[type]

def is_key_down(*keys):
    for key in keys:
        if key in down_keys: return True
    return False

def is_key_up(*keys):
    for key in keys:
        if key in up_keys: return True
    return False

def is_key_pressed(*keys):
    for key in keys:
        if key in pressed_keys: return True
    return False


def poll():
    "get events from queue. call in main loop"

    global down_keys, up_keys, pressed_keys

    down_keys = set()
    up_keys = set()

    for event in pygame.event.get():
        if event.type == KEYDOWN:
            down_keys.add(event.key)
            #safe_remove(up_keys, event.key)
            pressed_keys.add(event.key)
        elif event.type == KEYUP:
            #safe_remove(down_keys, event.key)
            up_keys.add(event.key)
            safe_remove(pressed_keys, event.key)

        for listener in listeners.get(event.type, set()):
            listener(event)


# utility functions
def safe_remove(container, item):
    if item in container: container.remove(item)


class Event(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class EventDispatcher(object):
    def __init__(self):
        self.event_listeners = {}

    def add_event_listener(self, type, listener):
        self.event_listeners.setdefault(type, set()).add(listener)

    def remove_event_listener(self, type, listener):
        if type not in self.event_listeners: return
        if listener not in self.event_listeners[type]: return
        self.event_listeners[type].remove(listener)
        if len(self.event_listeners[type]) == 0:
            del self.event_listeners[type]

    def dispatch(self, type, **kwargs):
        for listener in self.event_listeners.get(type, set()):
            listener(Event(type = type, **kwargs))
