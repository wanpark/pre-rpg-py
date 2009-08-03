# -*- coding:utf-8 -*-

import sys
import pygame
from pygame.locals import *
from rpg.constants import *
import rpg.event
import rpg.scene
import rpg.model
import rpg.lang
import rpg.menu
import rpg.draw

class GameScene(rpg.scene.Scene):
    def __init__(self):
        rpg.scene.Scene.__init__(self)
        self.cursor.margin = 5
        for player in rpg.model.get_players():
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
        for player in rpg.model.get_players():
            while self.view(player).is_transforming(): yield

        for player in rpg.model.get_players():
            sprite = self.view(player).intermission_sprite
            sprite.on_click = lambda e, p=player: self.open_menu(p)
            sprite.on_mouse_over = lambda e, p=player: self.select_player(p)
        self.add_event_listener(KEYDOWN, self.on_key_down)

        self.scene.add_view(self.scene.cursor)
        self.select_player(rpg.model.get_player(0))

        self.scene.add_view(self.navigator)
        self.navigator.rect.centery = self.view(rpg.model.get_player(1)).intermission_sprite.rect.centery
        self.navigator.on_click = rpg.lang.empty_function

        while not rpg.event.is_key_down(K_LEFT) and not self.navigator.is_clicked():
            yield

        for player in rpg.model.get_players():
            del self.view(player).intermission_sprite.on_click
        self.remove_event_listener(KEYDOWN, self.on_key_down)
        self.scene.remove_view(self.navigator)
        self.scene.remove_view(self.scene.cursor)

        for player in rpg.model.get_players():
            self.view(player).walk()

        for i in self.wait_generator(900): yield

        for player in rpg.model.get_players():
            self.view(player).stand()


        translates = []
        for enemy in rpg.model.get_stage().get_enemies():
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

        for player in rpg.model.get_players():
            self.view(player).transform()

        for player in rpg.model.get_players():
            while self.view(player).is_transforming(): yield

        self.setup_stage()

        self.scene.set_controller(CommandSelectController(self.scene))

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

    def setup_stage(self):
        rpg.model.get_stage().init()
        for character in rpg.model.get_stage().get_characters():
            self.scene.get_view_for(character).show_parameters()


class CommandSelectController(rpg.scene.Controller):

    def __init__(self, scene):
        super(CommandSelectController, self).__init__(scene)

        self.character = rpg.model.get_stage().get_actor()

        self.select_box = CommandSelectBox(self.character, self.scene.get_view_for(self.character))
        self.select_box.on_focus = self.on_focus_command
        self.select_box.on_select = self.on_select_command
        self.select_box.focus(self.select_box.buttons()[0])

    def enable(self):
        super(CommandSelectController, self).enable()
        self.scene.add_view(self.select_box)
        self.scene.add_view(self.scene.cursor)

    def disable(self):
        super(CommandSelectController, self).disable()
        self.scene.remove_view(self.select_box)
        self.scene.remove_view(self.scene.cursor)

    def on_focus_command(self, event):
        self.scene.cursor.point(event.button)

    def on_select_command(self, event):
        self.command = event.button.item
        self.scene.set_controller(TargetSelectController(
            self.scene, self.command.get_target_type(),
            self.on_select_target, self.on_cancel_target
        ))

    def on_select_target(self, targets):
        self.command.set_targets(targets)
        self.scene.set_controller(CommandExecuteController(self.scene, self.command))

    def on_cancel_target(self):
        self.scene.set_controller(self)

    def update(self):
        select = self.select_box
        if rpg.event.is_key_down(K_LEFT, *CANCEL_KEYS):
            pass
        elif rpg.event.is_key_down(K_RIGHT, *OK_KEYS):
            select.select(select.focused_button)
        elif rpg.event.is_key_down(K_UP):
            select.focus(select.up_button(select.focused_button))
        elif rpg.event.is_key_down(K_DOWN):
            select.focus(select.down_button(select.focused_button))


class CommandSelectBox(rpg.ui.RadioTable):

    def __init__(self, character, view):
        super(CommandSelectBox, self).__init__(cols = 1)
        self.character = character

        commands = self.character.get_commands()

        self.box = rpg.sprite.Sprite(pygame.Surface((105, 3 + 22 * len(commands))))
        self.box.image.fill(COLOR_BACKGROUND)
        rpg.draw.rounded_rect(self.box.image, self.box.rect.inflate(-1, -1))
        if view.is_flipped():
            self.box.rect.midright = view.sprite.rect.center
            self.box.rect.left -= 30
        else:
            self.box.rect.midleft = view.sprite.rect.center
            self.box.rect.left += 30
        self.add(self.box)

        for command in commands:
            button = rpg.ui.RadioButton(command.label, Rect(self.box.rect.left + 20, self.box.rect.top + 2, 80, 20), command)
            button.focus = rpg.lang.empty_function  # disable focus rect
            button.select = rpg.lang.empty_function  # disable select rect
            button.on_mouse_out = rpg.lang.empty_function  # disable unselect
            self.add(button)

class TargetSelectController(rpg.scene.Controller):
    def __init__(
        self, scene, target_type,
        on_select = rpg.lang.empty_function, on_cancel = rpg.lang.empty_function, on_focus = rpg.lang.empty_function
    ):
        super(TargetSelectController, self).__init__(scene)
        self.on_select = on_select
        self.on_cancel = on_cancel
        self.on_focus = on_focus
        self.focused_character = None

        self.cursors = {}
        for characters, position in [(rpg.model.get_stage().get_players(), 'left'), (rpg.model.get_stage().get_enemies(), 'right')]:
            for character in characters:
                cursor = rpg.ui.CursorSprite(position = position)
                cursor.point(self.scene.get_view_for(character).get_sprite())
                self.cursors[character] = cursor

        self.add_event_listener(MOUSEBUTTONUP, self.on_mouse_click)

    def get_nearlest_alive_character(self, character):
        if character.is_alive():
            return character
        friends = rpg.model.get_stage().get_friends(character)
        return self.get_nearlest_alive_character(friends[(character.index + 1) % len(friends)])

    def focus(self, character):
        character = self.get_nearlest_alive_character(character)
        if self.focused_character:
            self.scene.remove_view(self.get_cursor(self.focused_character))

        self.focused_character = character
        self.scene.add_view(self.get_cursor(self.focused_character))

        self.on_focus(character)

    def select(self, character):
        character = self.get_nearlest_alive_character(character)
        self.on_select([character])

    def get_cursor(self, character):
        return self.cursors[character]

    def enable(self):
        super(TargetSelectController, self).enable()

        for character in rpg.model.get_stage().get_characters():
            if character.is_alive():
                sprite = self.scene.get_view_for(character).get_sprite()
                sprite.on_click = lambda event, character = character: self.select(character)
                sprite.on_mouse_over = lambda event, character = character: self.focus(character)

        self.focus(rpg.model.get_stage().get_enemies()[0])

    def disable(self):
        super(TargetSelectController, self).disable()
        if self.focused_character:
            self.scene.remove_view(self.get_cursor(self.focused_character))
        for character in rpg.model.get_stage().get_characters():
            if character.is_alive():
                sprite = self.scene.get_view_for(character).get_sprite()
                del sprite.on_click
                del sprite.on_mouse_over

    def update(self):
        if not self.focused_character: return

        if rpg.event.is_key_down(*CANCEL_KEYS):
            self.on_cancel()
        elif rpg.event.is_key_down(*OK_KEYS):
            if self.focused_character:
                self.select(self.focused_character)
        if rpg.event.is_key_down(K_UP):
            friends = self.get_friends()
            self.focus(friends[(self.focused_character.index - 1) % len(friends)])
        elif rpg.event.is_key_down(K_DOWN):
            friends = self.get_friends()
            self.focus(friends[(self.focused_character.index + 1) % len(friends)])
        elif rpg.event.is_key_down(K_RIGHT, K_LEFT):
            rivals = self.get_rivals()
            self.focus(rivals[min([self.focused_character.index, len(rivals) - 1])])

    def on_mouse_click(self, event):
        if event.button == MOUSE_BUTTON_RIGHT:
            self.on_cancel()

    def get_friends(self):
        if self.focused_character.is_player():
            return rpg.model.get_stage().get_players()
        else:
            return rpg.model.get_stage().get_enemies()

    def get_rivals(self):
        if self.focused_character.is_player():
            return rpg.model.get_stage().get_enemies()
        else:
            return rpg.model.get_stage().get_players()


class CommandExecuteController(rpg.scene.CoroutineController):
    def __init__(self, scene, command):
        super(CommandExecuteController, self).__init__(scene)
        self.command = command

    def update_generator(self):
        if self.command.actor.is_enemy():
            serif = self.create_serif()
            self.scene.add_view(serif)
            for i in self.wait_generator(500): yield
            self.scene.remove_view(serif)

        self.command.do()

        self.scene.set_controller(get_command_effect_controller(self.scene, self.command))

    def create_serif(self):
        serif = rpg.sprite.Sprite(pygame.Surface((105, 20)))
        serif.image.fill(COLOR_BACKGROUND)
        rpg.draw.rounded_rect(serif.image, serif.rect.inflate(-1, -1))
        serif.image.blit(rpg.resource.font().render(self.command.label, False, COLOR_FOREGROUND), (5, 3))
        serif.rect.midleft = self.scene.get_view_for(self.command.actor).sprite.rect.center
        serif.rect.left += 30
        return serif


class TurnEndController(rpg.scene.CoroutineController):
    def update_generator(self):
        rpg.model.get_stage().finalize_turn()
        for character in rpg.model.get_stage().get_characters():
            self.scene.get_view_for(character).refresh()

        if rpg.model.get_stage().is_end():
            if rpg.model.get_stage().is_win():
                self.scene.set_controller(WinController(self.scene))
            else:
                pass
        else:
            if rpg.model.get_stage().get_actor().is_enemy():
                for i in self.wait_generator(300): yield
                self.scene.set_controller(CommandExecuteController(self.scene, rpg.model.get_stage().create_command()))
            else:
                self.scene.set_controller(CommandSelectController(self.scene))

class WinController(rpg.scene.CoroutineController):
    def update_generator(self):
        for enemy in rpg.model.get_stage().get_enemies():
            while self.view(enemy).is_transforming(): yield

        for enemy in rpg.model.get_stage().get_enemies():
            view = self.view(enemy)
            sprite = view.intermission_sprite
            sprite.fps = 20
            sprite.flip()
            view.walk()
            rpg.sprite.Translate(
                sprite,
                sprite.rect.topleft,
                (- sprite.rect.width, sprite.rect.top),
                500,
                on_finish = lambda e, enemy = enemy: self.scene.remove_view_for(enemy)
            )

        self.add_event_listener(KEYDOWN, self.on_key_down)
        self.add_event_listener(MOUSEBUTTONUP, self.on_click)

        old_levels = [player.get_level() for player in rpg.model.get_stage().get_players()]

        rpg.model.get_stage().finalize()

        messages = {}
        for player, old_level in zip(rpg.model.get_stage().get_players(), old_levels):
            message = []
            new_level = player.get_level()
            if new_level <= old_level: continue
            messages[player] = message
            if player.is_master():
                message.append(u'マスター！')
            else:
                message.append(u'レベルアップ！')
            for level in range(old_level, new_level):
                message.append(player.get_job().skill_for_level(level).label + u'を習得')
            if old_level == 0:
                for job in rpg.job.get_jobs():
                    if player.get_job() in job.requires and player.can_become(job):
                        message.append(job.label + u'になれる')

        while messages:
            for player, message in messages.items():
                serif = rpg.sprite.Sprite(rpg.resource.font(small = True).render(message.pop(0), False, COLOR_FOREGROUND))
                serif.rect.midbottom = self.view(player).sprite.rect.midbottom
                serif.rect.top -= 60
                self.add_view(serif)
                if not message: del messages[player]
            for i in self.wait_generator(1000): yield
            self.remove_all_views()

    def finish(self):
        self.remove_all_views()
        for player in rpg.model.get_stage().get_players():
            self.view(player).untransform()
        rpg.model.next_stage()
        self.scene.set_controller(IntervalController(self.scene))

    def on_key_down(self, event):
        if event.key in OK_KEYS or event.key in CANCEL_KEYS:
            self.finish()

    def on_click(self, event):
        self.finish()

def get_command_effect_controller(scene, command):
    controller_cls = getattr(
        sys.modules['rpg.game'], command.name.capitalize() + 'CommandEffectController',
        DefaultCommandEffectController
    )
    controller = controller_cls(scene)
    controller.command = command
    return controller

class DefaultCommandEffectController(rpg.scene.Controller):
    def update(self):
        self.scene.set_controller(TurnEndController(self.scene))

class BeatCommandEffectController(rpg.scene.CoroutineController):
    def update_generator(self):
        sprite = self.scene.get_view_for(self.command.targets[0]).sprite
        sprite.rect.left += 3
        for i in self.wait_generator(50): yield
        sprite.rect.left -= 6
        for i in self.wait_generator(50): yield
        sprite.rect.left += 6
        for i in self.wait_generator(50): yield
        sprite.rect.left -= 3
        for i in self.wait_generator(200): yield
        self.scene.set_controller(TurnEndController(self.scene))

class WatchCommandEffectController(rpg.scene.CoroutineController):
    def update_generator(self):
        sprite = self.scene.get_view_for(self.command.actor).sprite
        origin = sprite.rect.topleft
        image = sprite.image

        target_view = self.scene.get_view_for(self.command.targets[0])
        if target_view.is_flipped():
            sprite.rect.bottomright = target_view.sprite.rect.midbottom
            sprite.rect.left -= 30
        else:
            sprite.rect.bottomleft = target_view.sprite.rect.midbottom
            sprite.rect.left += 30
        if self.command.actor.is_player() == self.command.targets[0].is_player():
            sprite.image = pygame.transform.flip(sprite.image, True, False)

        for i in self.wait_generator(600): yield

        sprite.rect.topleft = origin
        sprite.image = image
        for i in self.wait_generator(200): yield

        self.scene.set_controller(TurnEndController(self.scene))
