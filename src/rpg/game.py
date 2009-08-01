# -*- coding:utf-8 -*-

import pygame
from pygame.locals import *
from rpg.constants import *
import rpg.event
import rpg.scene
import rpg.model
import rpg.lang
import rpg.menu

class GameScene(rpg.scene.Scene):
    def __init__(self):
        rpg.scene.Scene.__init__(self)

        for player in rpg.model.players():
            self.add_view_for(player, rpg.character.PlayerView(player))

        self.controller = IntervalController(self)

class IntervalController(rpg.scene.CoroutineController):
    def __init__(self, scene):
        rpg.scene.CoroutineController.__init__(self, scene)

        self.navigator = rpg.sprite.AnimationSprite(
            'arrow.png', 2,
            (SCREEN_RECT.width - 200, SCREEN_RECT.height / 2 - 10),
            3
        )

    def update_generator(self):
        for player in rpg.model.players():
            sprite = self.view(player).intermission_sprite
            sprite.on_click = lambda e, p=player: self.open_menu(p)
            sprite.on_mouse_over = lambda e, p=player: self.select_player(p)
        self.add_event_listener(KEYDOWN, self.on_key_down)

        self.scene.add_view(self.scene.cursor)
        self.select_player(rpg.model.player(0))

        self.scene.add_view(self.navigator)
        self.navigator.rect.centery = self.view(rpg.model.player(1)).intermission_sprite.rect.centery
        self.navigator.on_click = rpg.lang.empty_function

        while not rpg.event.is_key_down(K_LEFT) and not self.navigator.is_clicked():
            yield

        for player in rpg.model.players():
            del self.view(player).intermission_sprite.on_click
        self.remove_event_listener(KEYDOWN, self.on_key_down)
        self.scene.remove_view(self.navigator)
        self.scene.remove_view(self.scene.cursor)

        for player in rpg.model.players():
            self.view(player).walk()

        for i in self.wait_generator(900): yield

        for player in rpg.model.players():
            self.view(player).stand()

        rpg.model.create_enemies()

        translates = []
        for enemy in rpg.model.enemies():
            view = rpg.character.EnemyView(enemy)
            self.scene.add_view_for(enemy, view)
            rpg.sprite.Translate(
                view.sprite,
                (- view.sprite.rect.width, view.sprite.rect.top),
                view.sprite.rect.topleft,
                100
            )
            for i in self.wait_generator(60): yield

        for i in self.wait_generator(200): yield

        for player in rpg.model.players():
            self.view(player).transform()

        for player in rpg.model.players():
            while self.view(player).is_transforming(): yield

        #self.scene.set_controller(IntervalController(self.scene))

    def on_key_down(self, event):
        if event.key == K_DOWN:
            self.select_player(rpg.model.next_player(self.current_player))
        elif event.key == K_UP:
            self.select_player(rpg.model.prev_player(self.current_player))
        elif event.key in rpg.OK_KEYS or event.key == K_RIGHT:
            self.open_menu(self.current_player)

    def select_player(self, player):
        self.current_player = player
        self.scene.cursor.point(self.view(self.current_player).intermission_sprite)

    def open_menu(self, player):
        rpg.scene.switch_scene(rpg.menu.MenuScene(player))
