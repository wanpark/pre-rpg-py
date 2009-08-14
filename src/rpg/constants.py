# -*- coding:utf-8 -*-

import os
import pygame
from pygame.locals import *


# system constants

MOUSE_BUTTON_LEFT = 1
MOUSE_BUTTON_RIGHT = 3


# application constants

TEAM_PLAYER = 'player'
TEAM_ENEMY = 'enemy'

SEX_MALE = 'male'
SEX_FEMALE = 'female'
SEX_NONE = 'none'

LEARN_STATE_MASTER = 'master'
LEARN_STATE_FAMILIAR = 'familiar'
LEARN_STATE_NONE = 'none'

TARGET_NONE = 'none'
TARGET_ONE = 'one'
TARGET_PARTY = 'party'


# application setting

SCREEN_RECT = pygame.rect.Rect(100, 100, 400, 300)
FPS = 60
RESOURCE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'resource')

OK_KEYS = set((K_RETURN, K_x))
CANCEL_KEYS = set((K_BACKSPACE, K_z))
ESCAPE_KEYS = set((K_ESCAPE, ))
NEXT_KEYS = set((K_s, ))
PREV_KEYS = set((K_a, ))

COLOR_BACKGROUND = Color(255, 255, 255)
COLOR_FOREGROUND = Color(0, 0, 0)
COLOR_DISABLED = Color(180, 180, 180)

COLOR_MAX_HP = Color(225, 225, 225)
COLOR_REMAIN_HP = Color(100, 149, 237)
COLOR_LOST_HP = Color(139, 10, 80)
COLOR_WILL_LOST_HP = Color(200, 130, 180)

COLOR_USE_EP = Color(200, 130, 180)
