# -*- coding:utf-8 -*-

import os
import pygame
from pygame.locals import *
from rpg.constants import *

images = {}

def image(name):
    return images.setdefault(name, pygame.image.load(get_resouce_path(name)).convert_alpha())

fonts = {}
def font(small = False):
    size = 10 if small else 12
    if size in fonts: return fonts[size]
    fonts[size] = pygame.font.Font(get_resouce_path('bdfmplus.ttf'), size)
    return fonts[size]


def get_resouce_path(name):
    return os.path.join(RESOURCE_DIR, name)


def job_image(job, sex = SEX_NONE):
    if sex == SEX_FEMALE:
        name = job.name + '_female.png'
        if os.path.exists(get_resouce_path(name)):
            return image(name)
    return image(job.name + '.png')
