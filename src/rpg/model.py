# -*- coding:utf-8 -*-

from rpg.constants import *
import rpg.character
import rpg.stage

_players = []
_enemies = []

_stage = None

def init():
    rpg.model._players = [
        rpg.character.Player(0, 'boy', rpg.job.get_job('villager'), SEX_MALE),
        rpg.character.Player(1, 'girl', rpg.job.get_job('villager'), SEX_FEMALE),
        rpg.character.Player(2, 'ninja', rpg.job.get_job('villager'), SEX_MALE)
    ]
    rpg.model._stage  = rpg.stage.Stage1_1()


def get_players():
    return _players

def get_player(index):
    return _players[index]

def next_player(prev_player):
    return get_player((prev_player.index + 1) % len(get_players()))

def prev_player(next_player):
    return get_player((next_player.index - 1) % len(get_players()))

def get_stage():
    return _stage

def next_stage():
    rpg.model._stage  = rpg.stage.Stage1_1()
