# -*- coding:utf-8 -*-

import functional
from rpg.constants import *
import rpg.model
import rpg.job
import rpg.event

EP_CHANGED = 'ep_changed'

class Stage(rpg.event.EventDispatcher):    

    def __init__(self, enemies):
        super(Stage, self).__init__()
        self.enemies = enemies
        self.actor = self.get_players()[0]
        self.eps = { TEAM_PLAYER: 0, TEAM_ENEMY: 0 }

    def init(self):
        "call before battle start"
        for character in self.get_characters():
            character.clear_parameters()

    def finalize(self):
        for player in self.get_players():
            player.add_exp(1)

    def get_enemies(self):
        return self.enemies

    def get_players(self):
        return rpg.model.get_players()

    def get_characters(self):
        return self.get_players() + self.get_enemies()

    def get_friends(self, character):
        if character.is_player():
            return self.get_players()
        else:
            return self.get_enemies()

    def get_rivals(self, character):
        if character.is_player():
            return self.get_enemies()
        else:
            return self.get_players()

    def get_actor(self):
        return self.actor

    def next_actor(self, character = None):
        'dont call if self.is_end() == True'
        if not character: character = self.actor

        if character.is_player() and character.index < len(self.get_enemies()):
            actor = self.get_enemies()[character.index]
        else:
            actor = self.get_players()[(character.index + 1) % len(self.get_players())]

        if actor.is_alive():
            return actor
        else:
            return self.next_actor(actor)

    def finalize_turn(self):
        if self.is_end():
            self.actor = None
        else:
            self.actor = self.next_actor()

    def is_end(self):
        return self.is_win() or self.is_loose()

    def is_win(self):
        return functional.all(self.get_enemies(), lambda c: not c.is_alive())

    def is_loose(self):
        return functional.all(self.get_players(), lambda c: not c.is_alive())

    def get_ep(self, team):
        return self.eps[team]

    def set_ep(self, team, ep):
        if self.get_ep(team) == ep: return
        self.eps[team] = ep
        self.dispatch(EP_CHANGED, stage=self, team=team)

    def create_command(self):
        "override in subclass"
        pass


class Stage1_1(Stage):
    def __init__(self):
        super(Stage1_1, self).__init__([
            #rpg.character.Enemy(0, rpg.job.get_job('villager'), SEX_FEMALE),
            #rpg.character.Enemy(1, rpg.job.get_job('villager'), SEX_MALE),
            rpg.character.Enemy(0, rpg.job.get_job('cat'), SEX_FEMALE),
        ])

    def create_command(self):
        command = rpg.skill.get_skill('beat').create_command(self.get_actor())
        command.set_targets([self.get_target()])
        return command

    def get_target(self):
        players = [player for player in self.get_players() if player.is_alive()]

        for player in players:
            if player.get_job() is rpg.job.get_job('villager'):
                return player

        return players[0]
