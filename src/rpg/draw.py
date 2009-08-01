# -*- coding:utf-8 -*-

import math
import pygame
from pygame.locals import *

# http://www.mail-archive.com/pygame-users@seul.org/msg06800.html
def rounded_rect(
    surface,
    (posx, posy, dimensionx, dimensiony),
    width = 1, roundedness = 1,
    border_color = (0,0,0), fill_color = (255,255,255)
):
    for x in xrange(roundedness,0-1,-1):
        y = math.sqrt((roundedness**2)-(x**2))
        rect = (posx+(roundedness-x),
                posy+(roundedness-y),
                dimensionx-(2*(roundedness-x)),
                dimensiony-(2*(roundedness-y)))
        pygame.draw.rect(surface,border_color,rect,0)
    for x in xrange(roundedness-width,0-1,-1):
        y = math.sqrt(((roundedness-width)**2)-(x**2))
        rect = (posx+(roundedness-x),
                posy+(roundedness-y),
                dimensionx-(2*(roundedness-x)),
                dimensiony-(2*(roundedness-y)))
        pygame.draw.rect(surface,fill_color,rect,0)
