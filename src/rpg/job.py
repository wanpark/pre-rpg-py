# -*- coding:utf-8 -*-

import rpg.skill
import rpg.resource
import yaml

class Job(object):
    def __init__(self, name, label, max_hp, skills, traits, description):
        self.name = name
        self.label = label
        self.max_hp = max_hp
        self.skills = skills
        self.traits = traits
        self.description = description
        self.requires = []

    def level_and_current_exp_for_exp(self, exp):
        level = 0
        for skill in self.skills:
            if exp < skill.exp: break
            exp -= skill.exp
            level += 1
        return (level, exp)

    def level_for_exp(self, exp):
        return self.level_and_current_exp_for_exp(exp)[0]

    def current_exp_for_exp(self,exp):
        return self.level_and_current_exp_for_exp(exp)[1]

    def exp_for_level(self, level):
        if level >= len(self.skills): return 0
        return self.skills[level].exp

    def max_level(self):
        return len(self.skills)

    def available_skills(self, exp):
        return self.skills[0:min(self.level_for_exp(exp) + 1, len(self.skills))]

    def unavailable_skills(self, exp):
        level = self.level_for_exp(exp)
        return self.skills[level + 1:] if level + 1 < len(self.skills) else []


class Trait(object):
    def __init__(self, name, description):
        self.name = name
        self.description = description

_traits = [
    Trait('magician', u'魔法攻撃+50%'),
    Trait('nerd', u'物理ダメージ+50%'),
    Trait('dragon', u'炎ダメージ-50%'),
    Trait('recover_ep', u'毎ターンEP+1'),
    Trait('death_ep', u'死亡時EP+5'),
    Trait('villager', u'物理ダメージ+EP/2'),
]
_traits_for_name = dict([(trait.name, trait) for trait in _traits])

def get_traits():
    return _traits
def get_trait(name):
    return _traits_for_name[name]


_jobs = []
_jobs_for_name = {}

def load_jobs():
    global _jobs, _jobs_for_name

    infos = yaml.load(open(rpg.resource.get_resouce_path('jobs.yml')))
    _jobs = [Job(
        info['name'], info['label'], info['hp'],
        [rpg.skill.get_skill(skill) for skill in info.get('skills', [])],
        [get_trait(trait) for trait in info.get('traits', [])],
        info.get('description', '')
    ) for info in infos]
    _jobs_for_name = dict([(job.name, job) for job in _jobs])

    for info in infos:
        if 'requires' in info:
            _jobs_for_name[info['name']].requires = [_jobs_for_name[job] for job in info['requires']]

load_jobs()


def get_jobs():
    return _jobs
def get_job(name):
    return _jobs_for_name[name]
