# -*- coding:utf-8 -*-

import sys
from rpg.constants import *

class Skill(object):
    def __init__(self, name, label, exp, is_command, description):
        self.name = name
        self.label = label
        self.exp = exp
        self.is_command = is_command
        self.description = description

    def create_command(self, actor):
        if not self.is_command: return None
        command_cls = getattr(sys.modules['rpg.skill'], self.name.capitalize() + 'Command')
        command = command_cls()
        command.set_name(self.name)
        command.set_label(self.label)
        command.set_actor(actor)
        return command

class Command(object):
    def __init__(self, target_type):
        self.target_type = target_type

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

    def do(self):
        pass


class BeatCommand(Command):
    def __init__(self):
        super(BeatCommand, self).__init__(TARGET_ONE) 
    def do(self):
        self.targets[0].damage(3)

class WatchCommand(Command):
    def __init__(self):
        super(WatchCommand, self).__init__(TARGET_NONE) 
    def do(self):
        pass


_skills = dict([(skill.name, skill) for skill in [
    Skill('beat', u'なぐる', 1, True, u'物理攻撃3'),
    Skill('attack', u'こうげき', 1, True, u'物理攻撃5'),
    Skill('defence', u'ぼうぎょ', 1, True, u'1ターンの間ダメージ-50%'),
    Skill('fire', u'ファイア', 3, True, u'魔法攻撃10 EP-1'),
    Skill('watch', u'かんさつ', 1, True, u'敵を知り 己を知って ひとやすみ')
]])


def get_skills():
    return _skills.values()

def get_skill(name):
    return _skills[name]
