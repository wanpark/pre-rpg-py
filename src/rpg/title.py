# -*- coding:utf-8 -*-

import pygame
from pygame.locals import *
from rpg.constants import *
import rpg
import rpg.scene
import rpg.sprite
import rpg.event
import rpg.game
import rpg.resource

class TitleScene(rpg.scene.Scene):
    def __init__(self):
        rpg.scene.Scene.__init__(self)

        self.characters = rpg.sprite.Group(
            rpg.sprite.AnimationSprite('boy_walk.png', 4, (0, 0)),
            rpg.sprite.AnimationSprite('girl_walk.png', 4, (20, 0)),
            rpg.sprite.AnimationSprite('ninja_walk.png', 4, (40, 0))
        )
        self.characters.move_sprites(SCREEN_RECT.width, 200)
        self.button = self.create_start_button()
        self.add_view(self.characters, self.button)

        self.cursor.point(self.button)
        self.add_view(self.cursor)

    def create_start_button(self):
        button = rpg.sprite.Sprite()
        button.image = rpg.resource.font().render(u'スタート', False, (0, 0, 0))
        rect = button.image.get_rect()
        button.rect = rect.move((SCREEN_RECT.width - rect.width) / 2, 100)
        button.on_click = self.start_game
        return button

    def update(self):
        rpg.scene.Scene.update(self)

        if rpg.event.is_key_down(*OK_KEYS):
            self.start_game()
            return

        self.characters.move_sprites(-1, 0)
        if self.characters.sprites()[-1].rect.right < 0:
            self.characters.move_sprites(
                SCREEN_RECT.width - self.characters.sprites()[0].rect.left,
                0
            )

    def start_game(self, *args):
        rpg.model.init()
        rpg.scene.switch_scene(rpg.game.GameScene)
