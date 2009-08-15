# -*- coding:utf-8 -*-

import math
import pygame
from pygame.locals import *
from rpg.constants import *
import rpg
import rpg.sprite
import rpg.job
import rpg.resource
import rpg.event


class Character(rpg.event.EventDispatcher):

    JOB_CHANGED = 'job_changed'
    DAMAGED = 'damaged'

    def __init__(self, index, name, job, sex):
        super(Character, self).__init__()
        self.index = index
        self.name = name
        self.job = job
        self.sex = sex

        self.total_exps = {}
        self.active_learned_skills = []
        self.learned_skills = []

        self.clear_parameters()

    def get_job(self):
        return self.job

    def set_job(self, job):
        if self.job != job:
            self.job = job
            self.dispatch(self.JOB_CHANGED)

    def get_sex(self):
        return self.sex

    def get_max_hp(self):
        return self.get_job().max_hp

    def get_hp(self):
        return self.hp

    def is_alive(self):
        return self.hp > 0

    def clear_parameters(self):
        self.hp = self.get_max_hp()

    def can_become(self, job):
        for req in job.requires:
            if not self.is_familiar(req):
                return False
        return True

    def get_level(self, job = None):
        if not job: job = self.get_job()
        return job.level_for_exp(self.get_total_exp(job))

    def get_total_exp(self, job = None):
        if not job: job = self.get_job()
        return self.total_exps.get(job, 0)

    def add_exp(self, exp, job = None):
        if not job: job = self.get_job()
        old_level = self.get_level(job)
        self.total_exps[job] = self.get_total_exp(job) + exp
        new_level = self.get_level(job)
        for level in range(old_level, new_level):
            self.add_leaned_skill(job.skill_for_level(level))

    def get_current_exp(self, job = None):
        if not job: job = self.get_job()
        return job.current_exp_for_exp(self.get_total_exp(job))

    def is_familiar(self, job = None):
        if not job: job = self.get_job()
        return self.get_level(job) > 0

    def is_master(self, job = None):
        if not job: job = self.get_job()
        return self.get_level(job) >= job.max_level()

    def get_learn_state(self, job = None):
        if not job: job = self.get_job()
        if self.is_master(job): return LEARN_STATE_MASTER
        if self.is_familiar(job): return LEARN_STATE_FAMILIAR
        return LEARN_STATE_NONE

    def get_learned_skills(self):
        return self.learned_skills

    def add_leaned_skill(self, skill):
        if skill in self.learned_skills: return
        self.learned_skills.append(skill)
        self.add_active_learned_skill(skill)

    def add_active_learned_skill(self, skill):
        if self.can_add_skill() and skill in self.learned_skills:
            self.active_learned_skills.append(skill)

    def remove_skill(self, skill):
        self.active_learned_skills.remove(skill)

    def can_add_skill(self):
        return len(self.active_learned_skills) < self.get_skill_limit()

    def get_active_learned_skills(self):
        return self.active_learned_skills

    def get_skill_limit(self):
        return 4

    def get_skills(self):
        return rpg.lang.uniquify(self.get_job().available_skills(self.get_total_exp()) + self.get_active_learned_skills())

    def get_commands(self):
        return [skill.create_command(self) for skill in self.get_skills() if skill.is_command]

    def is_player(self):
        return False

    def is_enemy(self):
        return not self.is_player()

    def get_team(self):
        return TEAM_PLAYER if self.is_player() else TEAM_ENEMY

    def get_rival_team(self):
        return TEAM_ENEMY if self.is_player() else TEAM_PLAYER

    def damage(self, n):
        if n <= 0: return

        old_hp = self.hp
        self.hp -= n
        if self.hp < 0:
            self.hp = 0
        if self.hp != old_hp:
            self.dispatch(self.DAMAGED, hp_before_damage = old_hp, damage = n)

class Player(Character):
    def __init__(self, index, name, job, sex):
        Character.__init__(self, index, name, job, sex)

    def is_player(self):
        return True


class Enemy(Character):
    def __init__(self, index, job, sex):
        name = 'okashira' if sex == SEX_FEMALE else 'kaizoku'
        Character.__init__(self, index, name, job, sex)


class CharacterView(rpg.sprite.Group):
    def __init__(self, character):
        rpg.sprite.Group.__init__(self)
        self.character = character

        # for battle
        self.current_damage = 0
        self.hp_before_damage = 0
        self.hp_change = 0

        self.sprite = rpg.sprite.Sprite()
        self.on_job_change()

        self.parameters_sprite = rpg.sprite.Sprite(pygame.Surface((30, 50)))
        self.parameters_sprite.rect.bottomleft = (10, self.sprite.rect.bottom)
        if self.is_flipped():
            self.parameters_sprite.rect.right = SCREEN_RECT.width - self.parameters_sprite.rect.left

        self.character.add_event_listener(Character.JOB_CHANGED, self.on_job_change)
        self.character.add_event_listener(Character.DAMAGED, self.on_damaged)


        # for interval
        self._is_transforming = False;

        self.intermission_sprite = rpg.sprite.AnimationSprite(self.character.name + '_walk.png', 4)
        self.intermission_sprite.rect.midbottom = self.sprite.rect.midbottom

        self.transform_sprite = rpg.sprite.AnimationSprite(self.character.name + '_vanish.png', 7, fps = 15, repeat=False)
        self.transform_sprite.rect.midbottom = self.sprite.rect.midbottom

        self.untransform_sprite = rpg.sprite.AnimationSprite(self.character.name + '_appear.png', 7, fps = 15, repeat=False)
        self.untransform_sprite.rect.midbottom = self.sprite.rect.midbottom

    def get_sprite(self):
        return self.sprite if self.character.is_alive() else self.intermission_sprite

    def is_flipped(self):
        return False

    def on_job_change(self, *args):
        self.sprite.image = rpg.resource.job_image(self.character.get_job(), self.character.get_sex())
        self.sprite.rect = self.sprite.image.get_rect()
        self.sprite.rect.midbottom = (70, 90 + self.character.index * 90)
        if self.is_flipped():
            self.sprite.image = pygame.transform.flip(self.sprite.image, True, False)
            self.sprite.rect.centerx = SCREEN_RECT.width - self.sprite.rect.centerx

    def on_damaged(self, event):
        self.current_damage = event.damage
        self.hp_before_damage = event.hp_before_damage
        self.hp_change = 0
        self.update_parameters()

    def show_hp_change(self, change):
        self.hp_change = change
        self.update_parameters()

    def hide_hp_change(self):
        self.show_hp_change(0)

    def refresh(self):
        if self.current_damage or self.hp_change:
            self.current_damage = 0
            self.hp_change = 0
            self.update_parameters()
        if not self.character.is_alive() and self.sprite.is_displayed():
            self.untransform()

    def show_parameters(self):
        self.update_parameters()
        self.add(self.parameters_sprite)

    def hide_parameters(self):
        self.remove(self.parameters_sprite)

    def update_parameters(self):
        image = self.parameters_sprite.image
        image.fill(COLOR_BACKGROUND)

        hp_bar_width = 30
        hp_bar_y = image.get_height() - 1
        pygame.draw.line(image, COLOR_MAX_HP, (0, hp_bar_y), (hp_bar_width, hp_bar_y))

        displayed_hp = self.character.get_hp()

        # if self.hp_change > 0

        damage = self.current_damage
        damage_color = COLOR_LOST_HP
        if damage:
            displayed_hp = self.hp_before_damage
            damage_color = COLOR_LOST_HP
        elif self.hp_change < 0:
            damage = - self.hp_change
            damage_color = COLOR_WILL_LOST_HP

        if damage:
            hp_lost_rate = float(displayed_hp) / self.character.get_max_hp()
            pygame.draw.line(image, damage_color, (0, hp_bar_y), (math.floor(hp_lost_rate * hp_bar_width), hp_bar_y))

        if displayed_hp > damage:
            hp_remain_rate = float(displayed_hp - damage) / self.character.get_max_hp()
            pygame.draw.line(image, COLOR_REMAIN_HP, (0, hp_bar_y), (math.floor(hp_remain_rate * hp_bar_width), hp_bar_y))

        hp_label = rpg.resource.font(small = True).render('%d' % displayed_hp, False, COLOR_FOREGROUND)
        image.blit(hp_label, (0, hp_bar_y - 11))

        if damage:
            image.blit(
                rpg.resource.font(small = True).render(' - %d' % damage, False, damage_color),
                (hp_label.get_width(), hp_bar_y - 11)
            )
        # elif self.hp_change > 0

    def walk(self):
        self.intermission_sprite.set_current_frame(1)
        self.intermission_sprite.start()

    def stand(self):
        self.intermission_sprite.reset()

    def transform(self):
        self.stand()
        self.empty()
        self.add(self.transform_sprite)
        self.transform_sprite.reset()
        self.transform_sprite.start(self._finish_transforming)
        self._is_transforming = True

    def untransform(self):
        self.empty()
        self.add(self.untransform_sprite)
        self.untransform_sprite.reset()
        self.untransform_sprite.start(self._finish_untransforming)
        self._is_transforming = True

    def is_transforming(self):
        return self._is_transforming

    def _finish_transforming(self):
        self._is_transforming = False
        self.empty()
        self.add(self.sprite)

    def _finish_untransforming(self):
        self._is_transforming = False
        self.empty()
        self.add(self.intermission_sprite)
        self.stand()


class EnemyView(CharacterView):
    def __init__(self, player):
        CharacterView.__init__(self, player)
        self.add(self.sprite)

    def __getattr__(self, name):
        if name == 'enemy':
            return self.character
        else:
            raise AttributeError, name

class PlayerView(CharacterView):
    def __init__(self, player):
        CharacterView.__init__(self, player)
        self.add(self.intermission_sprite)
        self.stand()

    def __getattr__(self, name):
        if name == 'player':
            return self.character
        else:
            raise AttributeError, name
        
    def is_flipped(self):
        return True

