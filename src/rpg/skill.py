# -*- coding:utf-8 -*-

class Skill(object):
    def __init__(self, name, label, exp, is_command, description):
        self.name = name
        self.label = label
        self.exp = exp
        self.is_command = is_command
        self.description = description

_skills = dict([(skill.name, skill) for skill in [
    Skill('attack', u'こうげき', 1, True, u'物理攻撃 5'),
    Skill('defence', u'ぼうぎょ', 1, True, u'1ターンの間ダメージ-50%'),
    Skill('fire', u'ファイア', 2, True, u'魔法攻撃 10')
]])


def get_skills():
    return _skills.values()

def get_skill(name):
    return _skills[name]
