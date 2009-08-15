# -*- coding:utf-8 -*-

import sys
import math
from rpg.constants import *
import rpg.model

class Skill(object):
    def __init__(self, name, label, exp, is_command, description):
        self.name = name
        self.label = label
        self.exp = exp
        self.is_command = is_command
        self.description = description

    def create_command(self, actor):
        if not self.is_command: return None
        command_cls = getattr(sys.modules['rpg.skill'], self.name.capitalize() + 'Command', DefaultCommand)
        command = command_cls()
        command.set_name(self.name)
        command.set_label(self.label)
        command.set_actor(actor)
        return command

class Command(object):
    def __init__(self, target_type, ep_cost = 0):
        self.target_type = target_type
        self.ep_cost = ep_cost

    def get_target_type(self):
        return self.target_type

    def set_name(self, name):
        self.name = name

    def set_label(self, label):
        self.label = label

    def set_actor(self, actor):
        self.actor = actor

    def set_targets(self, targets):
        self.targets = targets

    def get_ep_cost(self):
        return self.ep_cost

    def get_stage(self):
        return rpg.model.get_stage()

    def get_damages(self):
        return {}

    def can_do(self):
        return self.get_ep_cost() <= self.get_stage().get_ep(self.actor.get_team())

    def do(self):
        self.get_stage().set_ep(self.actor.get_team(), self.get_stage().get_ep(self.actor.get_team()) - self.get_ep_cost())
        for target, damage in self.get_damages().iteritems():
            target.damage(damage)

class DefaultCommand(Command):
    def __init__(self):
        super(DefaultCommand, self).__init__(TARGET_NONE)


class BeatCommand(Command):
    def __init__(self):
        super(BeatCommand, self).__init__(TARGET_ONE)

    def get_damages(self):
        return dict([(target, modify_damage(3, DAMAGE_PHYSIC, self.actor, target)) for target in self.targets])

class WatchCommand(Command):
    def __init__(self):
        super(WatchCommand, self).__init__(TARGET_ONE)

class DefenceCommand(Command):
    def __init__(self):
        super(DefenceCommand, self).__init__(TARGET_NONE)

class FireCommand(Command):
    def __init__(self):
        super(FireCommand, self).__init__(TARGET_TEAM, ep_cost = 3)

    def get_damages(self):
        return dict([(target, modify_damage(3, DAMAGE_MAGIC, self.actor, target)) for target in self.targets])



def modify_damage(value, attr, actor, target):
    if attr & DAMAGE_PHYSIC:
        if actor.has_trait('villager'):
            value += math.floor(rpg.model.get_stage().get_ep(actor.get_team()) / 2)
        if target.has_trait('nerd'):
            value += math.floor(value / 2)
    if attr & DAMAGE_MAGIC:
        if actor.has_trait('magician'):
            value += math.floor(value / 2)
    return value


_skills = dict([(skill.name, skill) for skill in [
    Skill('beat', u'なぐる', 1, True, u'物理攻撃3'),
    Skill('attack', u'こうげき', 1, True, u'物理攻撃5'),
    Skill('defence', u'ぼうぎょ', 1, True, u'1ターンの間ダメージ-50%'),
    Skill('fire', u'ファイア', 3, True, u'全体魔法攻撃3 EP-3'),
    Skill('watch', u'かんさつ', 1, True, u'敵を知り 己を知って ひとやすみ')
]])


def get_skills():
    return _skills.values()

def get_skill(name):
    return _skills[name]
