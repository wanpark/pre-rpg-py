# -*- coding:utf-8 -*-

from rpg.constants import *
import rpg.character

_players = []
_enemies = []

def init():
    rpg.model._players = [
        rpg.character.Player(0, 'boy', SEX_MALE),
        rpg.character.Player(1, 'girl', SEX_FEMALE),
        rpg.character.Player(2, 'ninja', SEX_MALE)
    ]


def players():
    return _players

def player(index):
    return _players[index]

def next_player(prev_player):
    return player((prev_player.index + 1) % len(players()))

def prev_player(next_player):
    return player((next_player.index - 1) % len(players()))

def enemies():
    return _enemies

def create_enemies():
    rpg.model._enemies = [rpg.character.Enemy(i) for i in range(0, 3)]
