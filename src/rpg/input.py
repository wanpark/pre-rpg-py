# -*- coding:utf-8 -*-

"rpg.input - handle key inputs"

import sys
import pygame
from pygame.locals import *
from rpg.constants import *

down_keys = set()
up_keys = set()
pressed_keys = set()

def poll():
    "get events from queue. call in main loop"

    down_keys = set()
    up_keys = set()

    for event in pygame.event.get((KEYDOWN, KEYUP)):
        if event.type == KEYDOWN:
            down_keys.add(event.key)
            safe_remove(up_keys, event.key)
            pressed_keys.add(event.key)
        elif event.type == KEYUP:
            safe_remove(down_keys, event.key)
            up_keys.add(event.key)
            safe_remove(pressed_keys, event.key)

    expression = str((down_keys, up_keys, pressed_keys))
    global debug
    if debug != expression:
        print expression
        sys.stdout.flush()
        debug = expression

def is_down(key):
    return key in down_keys

def is_up(key):
    return key in up_keys

def is_pressed(key):
    return key in pressed_keys
        

# utility functions
def safe_remove(container, item):
    if item in container: container.remove(item)
