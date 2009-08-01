# -*- coding:utf-8 -*-

import sys
import pygame
from pygame.locals import *
from rpg.constants import *
import win32gui
import rpg.event
import rpg.scene
import rpg.title

# main

def main():
    pygame.init()

    win32gui.MoveWindow(
        pygame.display.get_wm_info()['window'],
        SCREEN_RECT.left, SCREEN_RECT.top,
        SCREEN_RECT.width, SCREEN_RECT.height,
        1
    )

    screen = pygame.display.set_mode(SCREEN_RECT.size)
    pygame.display.set_caption('pre-rpg')

    rpg.event.add_listener(QUIT, lambda event: sys.exit(0))

    rpg.scene.set_scene(rpg.title.TitleScene)

    clock = pygame.time.Clock()
    while True:
        clock.tick(FPS)
        try:
            rpg.event.poll()
            rpg.scene.do()
        except rpg.scene.SceneSwitchException, e:
            rpg.scene.set_scene(e.scene)
