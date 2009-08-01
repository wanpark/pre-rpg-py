# -*- coding:utf-8 -*-

import pygame
from pygame.locals import *
from rpg.constants import *
import rpg
import rpg.sprite
import rpg.job
import rpg.resource
import rpg.event

JOB_CHANGED = 'job_changed'

class Character(rpg.event.EventDispatcher):
    def __init__(self, index):
        super(Character, self).__init__()
        self.index = index
        self.job = rpg.job.get_job('villager')
        self.sex = SEX_NONE

    def get_job(self):
        return self.job

    def set_job(self, job):
        if self.job != job:
            self.job = job
            self.dispatch(JOB_CHANGED)

    def get_sex(self):
        return self.sex

class Player(Character):
    def __init__(self, index, name, sex):
        Character.__init__(self, index)
        self.name = name
        self.sex = sex
        self.total_exps = {}
        self.active_learned_skills = []
        self.learned_skills = [rpg.skill.get_skill('attack'), rpg.skill.get_skill('defence'), rpg.skill.get_skill('fire')]

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

    def get_current_exp(self, job = None):
        if not job: job = self.get_job()
        return job.current_exp_for_exp(self.get_total_exp(job))

    def is_familiar(self, job = None):
        if not job: job = self.get_job()
        return self.get_level(job) > 0

    def is_master(self, job = None):
        if not job: job = self.get_job()
        return self.get_level(job) >= job.max_level()

    def get_learned_skills(self):
        return self.learned_skills

    def add_skill(self, skill):
        if self.can_add_skill():
            self.active_learned_skills.append(skill)

    def remove_skill(self, skill):
        self.active_learned_skills.remove(skill)

    def can_add_skill(self):
        return len(self.active_learned_skills) < self.get_skill_limit()

    def get_active_learned_skills(self):
        return self.active_learned_skills

    def get_skill_limit(self):
        return 4


class Enemy(Character):
    def __init__(self, index):
        Character.__init__(self, index)


class CharacterView(rpg.sprite.Group):
    def __init__(self, character):
        rpg.sprite.Group.__init__(self)
        self.character = character

        self.sprite = rpg.sprite.Sprite()
        self.on_job_change()

        self.add(self.sprite)

        self.character.add_event_listener(JOB_CHANGED, self.on_job_change)

    def is_flipped(self):
        return False

    def on_job_change(self, *args):
        self.sprite.image = rpg.resource.job_image(self.character.get_job(), self.character.get_sex())
        self.sprite.rect = self.sprite.image.get_rect()
        self.sprite.rect.midleft = (20, 60 + self.character.index * 90)
        if self.is_flipped():
            self.sprite.image = pygame.transform.flip(self.sprite.image, True, False)
            self.sprite.rect.centerx = SCREEN_RECT.width - self.sprite.rect.centerx

class EnemyView(CharacterView):
    def __init__(self, player):
        CharacterView.__init__(self, player)

    def __getattr__(self, name):
        if name == 'enemy':
            return self.character
        else:
            raise AttributeError, name

class PlayerView(CharacterView):
    def __init__(self, player):
        CharacterView.__init__(self, player)

        self._is_transforming = False;

        self.intermission_sprite = rpg.sprite.AnimationSprite(self.player.name + '_walk.png', 4)
        self.intermission_sprite.rect.midbottom = self.sprite.rect.midbottom

        self.transform_sprite = rpg.sprite.AnimationSprite(self.player.name + '_vanish.png', 7, fps = 15, repeat=False)
        self.transform_sprite.rect.midbottom = self.sprite.rect.midbottom

        self.empty()
        self.add(self.intermission_sprite)
        self.stand()

    def __getattr__(self, name):
        if name == 'player':
            return self.character
        else:
            raise AttributeError, name

    def walk(self):
        self.intermission_sprite.set_current_frame(1)
        self.intermission_sprite.start()

    def stand(self):
        self.intermission_sprite.reset()

    def transform(self):
        self.stand()
        self.empty()
        self.add(self.transform_sprite)
        self.transform_sprite.start(self._finish_transforming)
        self._is_transforming = True

    def is_transforming(self):
        return self._is_transforming

    def _finish_transforming(self):
        self._is_transforming = False
        self.empty()
        self.add(self.sprite)
        
    def is_flipped(self):
        return True

