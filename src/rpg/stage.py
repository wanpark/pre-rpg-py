# -*- coding:utf-8 -*-

import functional
from rpg.constants import *
import rpg.model
import rpg.job
import rpg.event

EP_CHANGED = 'ep_changed'

class Stage(rpg.event.EventDispatcher):    

    def __init__(self, enemies, first_team):
        super(Stage, self).__init__()
        self.enemies = enemies
        self.actor = self.get_characters(first_team)[0]
        self.last_actors = {
            TEAM_PLAYER: None,
            TEAM_ENEMY: None
        }
        self.eps = { TEAM_PLAYER: 5, TEAM_ENEMY: 5 }

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

    def get_characters(self, team = None):
        if team == TEAM_PLAYER:
            return self.get_players()
        elif team == TEAM_ENEMY:
            return self.get_enemies()
        else:
            return self.get_players() + self.get_enemies()

    def get_friends(self, character):
        return self.get_characters(character.get_team())

    def get_rivals(self, character):
        return self.get_characters(character.get_rival_team())

    def get_actor(self):
        return self.actor

    def initialize_turn(self):
        if self.actor.has_trait('recover_ep'):
            self.set_ep(self.actor.get_team(), self.get_ep(self.actor.get_team()) + 1)

    def finalize_turn(self):
        if self.is_end():
            self.actor = None
        else:
            self.setup_next_actor()

    def setup_next_actor(self):
        'dont call if self.is_end() == True'
        self.last_actors[self.actor.get_team()] = self.actor

        actor = self.last_actors[self.actor.get_rival_team()]
        if not actor:
            actor = self.get_characters(self.actor.get_rival_team())[-1]
        friends = self.get_friends(actor)
        while True:
            actor = friends[(actor.index + 1) % len(friends)]
            if actor.is_alive():
                break

        self.actor = actor

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
        ], TEAM_PLAYER)

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
