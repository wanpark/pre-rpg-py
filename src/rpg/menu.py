# -*- coding:utf-8 -*-

import pygame
from pygame.locals import *
from rpg.constants import *
import rpg.scene
import rpg.character
import rpg.sprite
import rpg.game
import rpg.ui
import rpg.model
import rpg.job
import rpg.lang
import rpg.resource
import rpg.draw

class MenuScene(rpg.scene.Scene):

    def __init__(self, player):
        rpg.scene.Scene.__init__(self)

        self.player = player

        self.main_view = None

        self.cursor.margin = 5
        self.add_view(self.cursor)

        self.menu_view = MenuView(player)
        self.menu_view.radio.on_select = self.on_menu_select
        self.menu_view.radio.on_focus = self.on_menu_focus
        self.menu_view.radio.on_unfocus = self.on_menu_unfocus
        self.add_view(self.menu_view)

        self.job_view = JobView(player)
        self.job_view.table.on_select = self.on_job_select
        self.job_view.table.on_focus = self.on_job_focus
        self.job_view.table.on_unfocus = self.on_job_unfocus

        self.skill_view = SkillView(player)
        self.skill_view.job_table.on_focus = self.on_skill_focus
        self.skill_view.skill_table.on_focus = self.on_skill_focus
        self.skill_view.skill_table.on_select = self.on_skill_select
        self.skill_view.skill_table.on_unselect = self.on_skill_unselect

        self.set_mode('job')

        self.controllers = {
            'menu': MenuController(self),
            'job': JobController(self),
            'skill': SkillController(self),
        }
        self.set_controller_for('menu')

        self.add_event_listener(MOUSEBUTTONUP, self.on_mouse_click)


    def set_mode(self, mode):
        "mode = 'job' | 'skill'"

        view = self.job_view if mode == 'job' else self.skill_view
        if view == self.main_view: return

        if self.main_view:
            self.remove_view(self.main_view)

        self.main_view = view
        self.add_view(self.main_view)

    def set_controller_for(self, key):
        self.set_controller(self.controllers[key])


    def update(self):
        rpg.scene.Scene.update(self)
        if rpg.event.is_key_down(*ESCAPE_KEYS):
            rpg.scene.switch_scene(rpg.game.GameScene)

    def on_mouse_click(self, event):
        if event.button == MOUSE_BUTTON_RIGHT:
            rpg.scene.switch_scene(rpg.game.GameScene)

    def on_menu_select(self, event):
        self.set_mode(event.button.item)

    def on_menu_focus(self, event):
        self.unfocus_main_view()
        self.set_controller_for('menu')
        self.cursor.point(event.button)

    def on_menu_unfocus(self, event):
        self.set_controller_for('menu')
        self.cursor.point(self.menu_view.radio.selected_button)

    def on_job_focus(self, event):
        self.job_view.update_info()
        self.set_controller_for('job')
        self.cursor.point(event.button)

    def on_job_select(self, event):
        self.player.set_job(event.button.item)
        self.skill_view.update_tables()

    def on_job_unfocus(self, event):
        self.job_view.update_info()
        self.set_controller_for('job')
        self.cursor.point(self.job_view.table.selected_button)

    def on_skill_focus(self, event):
        other_table = self.skill_view.job_table if event.target == self.skill_view.skill_table else self.skill_view.skill_table
        other_table.unfocus()
        self.cursor.point(event.target.focused_button)
        self.controllers['skill'].target_table = event.target
        self.set_controller_for('skill')
        self.skill_view.update_info()

    def on_skill_select(self, event):
        self.player.add_skill(event.button.item)
        self.skill_view.update_remain_label()

    def on_skill_unselect(self, event):
        self.player.remove_skill(event.button.item)
        self.skill_view.update_remain_label()


    def unfocus_main_view(self):
        self.job_view.table.unfocus()
        self.skill_view.job_table.unfocus()
        self.skill_view.skill_table.unfocus()


class MenuController(rpg.scene.Controller):
    def enable(self):
        self.scene.cursor.point(self.scene.menu_view.radio.focused_or_selected_button())

    def update(self):
        radio = self.scene.menu_view.radio
        if rpg.event.is_key_down(K_LEFT, *CANCEL_KEYS):
            rpg.scene.switch_scene(rpg.game.GameScene)
        elif rpg.event.is_key_down(K_RIGHT, *OK_KEYS):
            button = radio.focused_or_selected_button()
            radio.select(button)
            self.scene.set_controller_for(button.item)
        elif rpg.event.is_key_down(K_UP):
            radio.unfocus()
            radio.select(radio.prev_button(radio.focused_or_selected_button()))
            self.scene.cursor.point(radio.selected_button)
        elif rpg.event.is_key_down(K_DOWN):
            radio.unfocus()
            radio.select(radio.next_button(radio.focused_or_selected_button()))
            self.scene.cursor.point(radio.selected_button)

class JobController(rpg.scene.Controller):
    def enable(self):
        table = self.scene.job_view.table
        self.scene.cursor.point(table.focused_or_selected_button())

    def disable(self):
        #self.scene.view.job_view.table.unfocus()
        pass

    def update(self):
        table = self.scene.job_view.table
        if rpg.event.is_key_down(*CANCEL_KEYS):
            table.unfocus()
            self.scene.set_controller_for('menu')
        elif rpg.event.is_key_down(*OK_KEYS):
            if table.focused_or_selected_button().enabled:
                table.select(table.focused_or_selected_button())
                #self.scene.set_controller_for('menu')
        elif rpg.event.is_key_down(K_UP):
            table.focus(table.up_button(table.focused_or_selected_button()))
        elif rpg.event.is_key_down(K_DOWN):
            table.focus(table.down_button(table.focused_or_selected_button()))
        elif rpg.event.is_key_down(K_LEFT):
            table.focus(table.left_button(table.focused_or_selected_button()))
        elif rpg.event.is_key_down(K_RIGHT):
            table.focus(table.right_button(table.focused_or_selected_button()))

class SkillController(rpg.scene.Controller):
    def __init__(self, *args, **kwargs):
        super(SkillController, self).__init__(*args, **kwargs)
        if len(self.scene.skill_view.skill_table.buttons()) > 0:
            self.target_table = self.scene.skill_view.skill_table
        else:
            self.target_table = self.scene.skill_view.job_table

    def enable(self):
        if not self.target_table.focused_button:
            self.target_table.focus(self.target_table.buttons()[0])

    def disable(self):
        self.scene.skill_view.update_info()

    def update(self):
        if rpg.event.is_key_down(*CANCEL_KEYS):
            self.target_table.unfocus()
            self.scene.set_controller_for('menu')
        elif rpg.event.is_key_down(*OK_KEYS):
            self.target_table.toggle(self.target_table.focused_button)
        elif rpg.event.is_key_down(K_LEFT):
            self.target_table.focus(self.target_table.left_button(self.target_table.focused_button))
        elif rpg.event.is_key_down(K_RIGHT):
            self.target_table.focus(self.target_table.right_button(self.target_table.focused_button))
        elif rpg.event.is_key_down(K_UP):
            next_button = self.target_table.up_button(self.target_table.focused_button, loop = False)
            if self.target_table == self.scene.skill_view.skill_table and next_button == self.target_table.focused_button:
                self.target_table.unfocus()
                self.target_table = self.scene.skill_view.job_table
                self.target_table.focus(self.target_table.buttons()[0])
            else:
                self.target_table.focus(next_button)
        elif rpg.event.is_key_down(K_DOWN):
            next_button = self.target_table.up_button(self.target_table.focused_button, loop = False)
            if self.target_table == self.scene.skill_view.job_table and next_button == self.target_table.focused_button:
                if len(self.scene.skill_view.skill_table.buttons()):
                    self.target_table.unfocus()
                    self.target_table = self.scene.skill_view.skill_table
                    self.target_table.focus(self.target_table.buttons()[0])
            else:
                self.target_table.focus(next_button)


class MenuView(rpg.sprite.CompositeGroup):

    def __init__(self, player):
        rpg.sprite.CompositeGroup.__init__(self)
        self.player = player

        self.character_sprite = rpg.sprite.Sprite(self.player.name + '.png')
        self.character_sprite.rect.move_ip(35, 10)
        self.add(self.character_sprite)

        self.radio = rpg.ui.RadioGroup(
            rpg.ui.RadioButton(u'クラス', pygame.rect.Rect(0, 0, 50, 20), 'job'),
            rpg.ui.RadioButton(u'スキル', pygame.rect.Rect(0, 22, 50, 20), 'skill')
        )
        self.radio.select_for('job')
        self.radio.move_sprites(20, 60)
        self.add(self.radio)

class JobView(rpg.sprite.CompositeGroup):

    def __init__(self, player):
        rpg.sprite.CompositeGroup.__init__(self)
        self.player = player

        separator = rpg.sprite.Sprite(pygame.Surface((300, 1)))
        separator.image.fill((255, 255, 255))
        pygame.draw.line(separator.image, (0, 0, 0), (0, 0), (270, 0))
        separator.rect.topleft = (100, 141)
        self.add(separator)

        self.table = rpg.ui.RadioTable(cols = 3)
        for job in rpg.job.get_jobs():
            button = JobTableRadioButton(
                job.label, pygame.rect.Rect(100, 150, 80, 20),
                item = job, enabled = self.player.can_become(job),
                learn_state = self.player.get_learn_state(job)
            )
            button.on_mouse_out = rpg.lang.empty_function
            self.table.add(button)
        self.table.select_for(self.player.get_job())
        self.add(self.table)

        self.info = rpg.sprite.Sprite(pygame.Surface((280, 140)))
        self.info.rect.topleft = (100, 0)
        self.update_info()
        self.add(self.info)

    def update_info(self):
        job = self.table.focused_or_selected_button().item
        self.info.image.fill(Color('white'))

        job_image = rpg.resource.job_image(job, self.player.get_sex())
        rect = job_image.get_rect()
        rect.midbottom = (40, 80)
        self.info.image.blit(job_image, rect)

        self.info.image.blit(rpg.resource.font().render(u'HP %3d' % job.max_hp, False, (0, 0, 0)), (10, 90))
        self.info.image.blit(rpg.resource.font().render(u'Lv  %2d' % self.player.get_level(job), False, (0, 0, 0)), (10, 105))
        if not self.player.is_master(job):
            self.info.image.blit(rpg.resource.font().render(u'Exp %2d / %d' % (self.player.get_current_exp(job), job.exp_for_level(self.player.get_level(job))), False, (0, 0, 0)), (10, 120))

        for i, trait in enumerate(job.traits):
            self.info.image.blit(rpg.resource.font().render(trait.description, False, (0, 0, 0)), (100, 20 + i * 15))

        for i, line in enumerate(job.description.split('\n')):
            self.info.image.blit(rpg.resource.font().render(line, False, (0, 0, 0)), (100, 90 + i * 15))


        for button in self.table.buttons():
            button.set_required(False)
        for req in job.requires:
            self.table.button_for(req).set_required(True)

class JobTableRadioButton(rpg.ui.RadioButton):
    def __init__(self, *args, **kwargs):
        self.learn_state = kwargs.pop('learn_state', LEARN_STATE_NONE)
        self.required = False
        super(JobTableRadioButton, self).__init__(*args, **kwargs)

    def set_required(self, b):
        if b != self.required:
            self.required = b
            self.draw_image()

    def draw_image(self):
        self.image.fill((255, 255, 255))
 
        if self.selected or self.focused:
            border_color = (0, 0, 0) if self.selected else COLOR_DISABLED
            rpg.draw.rounded_rect(
                self.image, self.image.get_rect().inflate(-2, -2),
                border_color = border_color
            )
 
        label_color = (0, 0, 0) if self.enabled else COLOR_DISABLED
        label_image = rpg.resource.font().render(self.label, False, label_color)
        self.image.blit(label_image, (5, (self.rect.height - label_image.get_rect().height) / 2))
 
        modify_label = self.get_modifier_label()
        if modify_label:
            modify_color = COLOR_DISABLED if self.learn_state == LEARN_STATE_NONE else (0, 0, 0)
            self.image.blit(
                rpg.resource.font().render(modify_label, False, modify_color),
                (5 + label_image.get_width(), (self.rect.height - label_image.get_rect().height) / 2)
            )

    def get_modifier_label(self):
        if self.learn_state == LEARN_STATE_MASTER:
            return u'★' if self.required else u'☆'
        elif self.learn_state == LEARN_STATE_FAMILIAR:
            return u'●' if self.required else u'○'
        elif self.required:
            return u'●'
        return ''            

class SkillView(rpg.sprite.CompositeGroup):
    def __init__(self, player):
        rpg.sprite.CompositeGroup.__init__(self)
        self.player = player

        separator = rpg.sprite.Sprite(pygame.Surface((300, 1)))
        separator.image.fill((255, 255, 255))
        pygame.draw.line(separator.image, (0, 0, 0), (0, 0), (270, 0))
        separator.rect.topleft = (100, 36)
        self.add(separator)

        job_label = rpg.sprite.Sprite(pygame.Surface((200, 15)))
        job_label.rect.topleft = (100, 45)
        job_label.image.fill((255, 255, 255))
        job_label.image.blit(rpg.resource.font().render(u'クラススキル', False, (0, 0, 0)), (0, 0))
        self.add(job_label)

        self.job_table = rpg.ui.ToggleTable(cols = 3)
        self.job_table.toggle = self.job_table.select = rpg.lang.empty_function  # disable select
        
        self.add(self.job_table)

        skill_label = rpg.sprite.Sprite(pygame.Surface((60, 15)))
        skill_label.rect.topleft = (100, 100)
        skill_label.image.fill((255, 255, 255))
        skill_label.image.blit(rpg.resource.font().render(u'習得スキル', False, (0, 0, 0)), (0, 0))
        self.add(skill_label)

        self.remain_label = rpg.sprite.Sprite(pygame.Surface((100, 15)))
        self.remain_label.rect.topleft = (180, 100)
        self.add(self.remain_label)

        self.skill_table = SkillSkillToggleTable(cols = 3, player = self.player)
        for skill in self.player.get_learned_skills():
            button = rpg.ui.ToggleButton(skill.label, pygame.rect.Rect(100, 120, 80, 20), skill)
            if rpg.lang.exists_in(self.player.get_active_learned_skills(), skill):
                button.select()
            button.on_mouse_out = rpg.lang.empty_function
            self.skill_table.add(button)
        self.add(self.skill_table)

        self.update_tables()
        self.update_remain_label()

        self.info = rpg.sprite.Sprite(pygame.Surface((280, 20)))
        self.info.rect.topleft = (100, 15)
        self.info.image.fill((255, 255, 255))
        self.update_info()
        self.add(self.info)

    def update_info(self):
        self.info.image.fill((255, 255, 255))

        focused = self.job_table.focused_button or self.skill_table.focused_button
        if not focused: return

        skill = focused.item
        self.info.image.blit(rpg.resource.font().render(skill.description, False, (0, 0, 0)), (0, 0))
        

    def update_tables(self):
        self.job_table.empty()
        for skill in self.player.get_job().available_skills(self.player.get_total_exp()):
            button = rpg.ui.RadioButton(skill.label, pygame.rect.Rect(100, 65, 80, 20), skill)
            button.on_mouse_out = rpg.lang.empty_function
            self.job_table.add(button)
        for skill in self.player.get_job().unavailable_skills(self.player.get_total_exp()):
            button = rpg.ui.RadioButton(skill.label, pygame.rect.Rect(100, 65, 80, 20), skill, enabled = False)
            button.on_mouse_out = rpg.lang.empty_function
            self.job_table.add(button)

    def update_remain_label(self):
        self.remain_label.image.fill(Color('white'))
        label = "%d / %d" % (len(self.player.get_active_learned_skills()), self.player.get_skill_limit())
        self.remain_label.image.blit(rpg.resource.font().render(label, False, Color('black')), (0, 0))

class SkillSkillToggleTable(rpg.ui.ToggleTable):
    def __init__(self, *args, **kwargs):
        self.player = kwargs.pop('player')
        super(SkillSkillToggleTable, self).__init__(*args, **kwargs)

    def select(self, *args, **kwargs):
        if not self.player.can_add_skill(): return
        super(SkillSkillToggleTable, self).select(*args, **kwargs)

