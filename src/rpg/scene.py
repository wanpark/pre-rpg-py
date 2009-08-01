# -*- coding:utf-8 -*-

import pygame
from pygame.locals import *
import rpg
import rpg.sprite
import rpg.loader
import rpg.event
import rpg.model
import rpg.lang
import rpg.ui

class SceneSwitchException(Exception):
    def __init__(self, scene):
        self.scene = scene

class EventListenable(object):
    def __init__(self):
        self.event_listeners = {}

    def add_event_listener(self, type, listener):
        self.event_listeners.setdefault(type, set()).add(listener)
        rpg.event.add_listener(type, listener)

    def remove_event_listener(self, type, listener):
        if type not in self.event_listeners: return
        if listener not in self.event_listeners[type]: return
        self.event_listeners[type].remove(listener)
        if len(self.event_listeners[type]) == 0:
            del self.event_listeners[type]
        rpg.event.remove_listener(type, listener)

    def enable(self):
        for type, listeners in self.event_listeners.iteritems():
            for listener in listeners:
                rpg.event.add_listener(type, listener)

    def disable(self):
        for type, listeners in self.event_listeners.iteritems():
            for listener in listeners:
                rpg.event.remove_listener(type, listener)


class Scene(EventListenable, rpg.lang.Singleton):
    def __init__(self):
        super(Scene, self).__init__()
        screen = pygame.display.get_surface()
        self.background = pygame.Surface(screen.get_size())
        self.background.fill((255, 255, 255))

        self.views = {}
        self.group = rpg.sprite.SceneGroup(self)
        self.controller = None

        self.cursor = rpg.ui.CursorSprite()

    def clear(self, screen):
        self.group.clear(screen, self.background)

    def update(self):
        self.group.update()
        if self.controller:
            self.controller.update()

    def render(self, screen):
        dirties = self.group.draw(screen)
        pygame.display.update(dirties)

    def set_controller(self, controller):
        if controller == self.controller: return
        if self.controller:
            self.controller.disable()
        self.controller = controller
        self.controller.enable()


    def add_view(self, *view):
        self.group.add(*view)

    def add_view_for(self, key, view):
        self.views[key] = view
        self.group.add(view)

    def get_view_for(self, key):
        return self.views.get(key, None)

    def remove_view(self, *view):
        self.group.remove(*view)

    def remove_view_for(self, key):
        if key in self.views:
            self.group.remove(self.views[key])
            del self.views[key]

    def clear_views(self):
        self.views = {}
        self.group.empty()

    def enable(self):
        super(Scene, self).enable()
        self.group.refresh_display()
        if self.controller:
            self.controller.enable()

    def disable(self):
        super(Scene, self).disable()
        if self.controller:
            self.controller.disable()


class Controller(EventListenable):
    def __init__(self, scene):
        super(Controller, self).__init__()
        self.scene = scene
        self.event_listeners = {}

    def update(self):
        pass

    def view(self, key):
        return self.scene.get_view_for(key)


class CoroutineController(Controller):
    def __init__(self, scene):
        Controller.__init__(self, scene)
        self.generator = None
        self.stopped = False

    def update(self):
        if self.stopped: return

        if not self.generator:
            self.generator = self.update_generator()

        try:
            self.generator.next()
        except StopIteration:
            self.stopped = True

    def update_generator(self):
        yield

    def wait_generator(self, ms):
        limit = pygame.time.get_ticks() + ms
        while limit > pygame.time.get_ticks():
            yield


_current_scene = None
def switch_scene(scene):
    if type(scene) == type: scene = scene.instance()
    raise SceneSwitchException, scene
def get_current_scene():
    return _current_scene
def set_scene(scene):
    if type(scene) == type: scene = scene.instance()
    if _current_scene:
        rpg.scene._current_scene.disable()
    rpg.scene._current_scene = scene
    scene.enable()

def do():
    screen = pygame.display.get_surface()
    _current_scene.clear(screen)
    _current_scene.update()
    _current_scene.render(screen)

