# -*- coding:utf-8 -*-

import Image
import pygame
from pygame.locals import *
from rpg.constants import *

def blend_color(image, color, alpha):
    mask = Image.new('RGB', image.get_size(), (int(color.r), int(color.g), int(color.b)))
    blended = Image.blend(pygame_to_pil(image), mask, alpha)
    blended = pil_to_pygame(blended)
    blended.set_colorkey(blended.get_at((0, 0)))
    return blended.convert()

def pygame_to_pil(image):
    return Image.fromstring('RGB', image.get_size(), pygame.image.tostring(image, 'RGB'))

def pil_to_pygame(image):
    return pygame.image.fromstring(image.tostring(), image.size, 'RGB')
