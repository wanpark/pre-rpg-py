# -*- coding:utf-8 -*-

import os
import pygame
from pygame.locals import *

# system constants

MOUSE_BUTTON_LEFT = 1
MOUSE_BUTTON_RIGHT = 3

# application setting

SCREEN_RECT = pygame.rect.Rect(100, 100, 400, 300)
FPS = 60
RESOURCE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'resource')

OK_KEYS = set((K_RETURN, K_x))
CANCEL_KEYS = set((K_BACKSPACE, K_z))
ESCAPE_KEYS = set((K_ESCAPE, ))
NEXT_KEYS = set((K_s, ))
PREV_KEYS = set((K_a, ))

COLOR_DISABLED = Color(180, 180, 180)
COLOR_HIGHLIGHT = Color(225, 225, 225)

SEX_MALE = 'male'
SEX_FEMALE = 'female'
SEX_NONE = 'none'
