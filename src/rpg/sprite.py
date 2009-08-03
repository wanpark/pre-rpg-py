# -*- coding:utf-8 -*-

import math
import pygame
from pygame.locals import *
from rpg.constants import *
import rpg.resource
import rpg.event
import rpg.lang

def sprites_from_groups(groups):
    return reduce(lambda sprites, group: sprites + group.sprites(), groups, [])

def add_to_clickable(scene_group, *sprites):
    if not scene_group: return
    for sprite in sprites:
        if hasattr(sprite, 'on_click'):
            scene_group.clickables.add(sprite)

def remove_from_clickable(scene_group, *sprites):
    if not scene_group: return
    for sprite in sprites:
        if hasattr(sprite, 'on_click'):
            scene_group.clickables.remove(sprite)



class Group(pygame.sprite.OrderedUpdates):
    def __init__(self, *sprites):
        self.parents = set()
        super(Group, self).__init__(*sprites)

    def scene_group(self):
        for group in self.parents:
            scene = group.scene_group()
            if scene: return scene
        return None

    def move_sprites(self, x, y):
        for sprite in self.sprites():
            sprite.rect.move_ip(x, y)

    def add(self, *sprites):
        super(Group, self).add(*sprites)
        add_to_clickable(self.scene_group(), *sprites)

    def remove(self, *sprites):
        remove_from_clickable(self.scene_group(), *sprites)
        super(Group, self).remove(*sprites)


class CompositeGroup(object):
    def __init__(self, *groups):
        self.parents = set()
        self.default_group = Group()
        self.default_group.parents.add(self)
        self.groups = []
        self.add(*groups)
        self.needs_refresh_display = True

    def scene_group(self):
        for group in self.parents:
            scene = group.scene_group()
            if scene: return scene
        return None

    def move_sprites(self, x, y):
        for sprite in self.sprites():
            sprite.rect.move_ip(x, y)

    def get_groups(self):
        return self.groups + [self.default_group]

    def add(self, *groups):
        for group in groups:
            if isinstance(group, pygame.sprite.Sprite):
                self.default_group.add(group)
            else:
                group.parents.add(self)
                self.groups.append(group)
                self.needs_refresh_display = True
        add_to_clickable(self.scene_group(), *sprites_from_groups(groups))

    def remove(self, *groups):
        remove_from_clickable(self.scene_group(), *sprites_from_groups(groups))
        for group in groups:
            if isinstance(group, pygame.sprite.Sprite):
                self.default_group.remove(group)
            else:
                group.parents.remove(self)
                self.groups.remove(group)
                self.needs_refresh_display = True

    def sprites(self):
        return sprites_from_groups(self.groups)

    def update(self):
        for group in self.get_groups():
            group.update()

    def draw(self, screen):
        dirty_rects = []
        for group in self.get_groups():
            rect = group.draw(screen)
            if rect:
                dirty_rects += rect

        if self.needs_refresh_display:
            self.needs_refresh_display = False
            return [screen.get_rect()]
        else:
            return dirty_rects

    def clear(self, screen, background = None):
        if background == None and hasattr(self, 'background'):
            background = self.background

        if not background: return

        if self.needs_refresh_display:
            screen.blit(background, (0, 0))
        else:
            for group in self.get_groups():
                group.clear(screen, background)

    def empty(self):
        self.remove(*self.groups)
        self.default_group.empty()
        self.needs_refresh_display = True

    def refresh_display(self):
        self.needs_refresh_display = True


class SceneGroup(CompositeGroup):
    def __init__(self, scene):
        CompositeGroup.__init__(self)
        self.clickables = ClickableGroup(scene)

    def update(self):
        CompositeGroup.update(self)
        self.clickables.update()

    def empty(self):
        CompositeGroup.empty(self)
        self.clickables.empty()

    def refresh_display(self):
        CompositeGroup.refresh_display(self)
        self.clickables.refresh()

    def scene_group(self):
        return self
    

class ClickableGroup(Group):
    def __init__(self, listenable):
        Group.__init__(self)

        self.overed_sprite = None
        self.needs_update_over = True
        pygame.mouse.set_cursor(*pygame.cursors.arrow)

        self.clicked_sprites = set()
        self.now_clicked = False

        # add listener to EventListenable, not to global.
        listenable.add_event_listener(MOUSEBUTTONUP, self.on_click)
        listenable.add_event_listener(MOUSEMOTION, self.on_mouse_motion)

    def is_clicked(self, sprite):
        return sprite in self.clicked_sprites

    def update(self):
        # when sprite is clicked, pass status only one update cycle
        if self.now_clicked:
            self.now_clicked = False
        else:
            self.clicked_sprites = set()

        if self.needs_update_over:
            overed = self.collidepoint(pygame.mouse.get_pos())

            if self.overed_sprite and self.overed_sprite != overed:
                if hasattr(self.overed_sprite, 'on_mouse_out'):
                    self.overed_sprite.on_mouse_out({})

            if overed:
                if not self.overed_sprite:
                    pygame.mouse.set_cursor(*pygame.cursors.broken_x)
                if overed != self.overed_sprite:
                    if hasattr(overed, 'on_mouse_over'):
                        overed.on_mouse_over({})
                self.overed_sprite = overed
            else:
                if self.overed_sprite:
                    pygame.mouse.set_cursor(*pygame.cursors.arrow)
                    self.overed_sprite = None
            self.needs_update_over = False

    def collidepoint(self, p):
        for sprite in self.sprites():
            if sprite.rect.collidepoint(p):
                return sprite
        return False

    def on_click(self, event):
        if event.button == MOUSE_BUTTON_RIGHT: return

        clicked = self.collidepoint(pygame.mouse.get_pos())
        if clicked:
            self.now_clicked = True
            self.clicked_sprites.add(clicked)
            if hasattr(clicked, 'on_click'):
                clicked.on_click(event)

    def on_mouse_motion(self, event):
        self.needs_update_over = True

    def add(self, *sprites):
        Group.add(self, *sprites)
        self.needs_update_over = True

    def remove(self, *sprites):
        Group.remove(self, *sprites)
        self.needs_update_over = True

    def empty(self):
        Group.empty(self)
        self.needs_update_over = True

    def refresh(self):
        if self.overed_sprite:
            if hasattr(self.overed_sprite, 'on_mouse_out'):
                self.overed_sprite.on_mouse_out({})
            self.overed_sprite = None
        pygame.mouse.set_cursor(*pygame.cursors.arrow)
        
        self.needs_update_over = True


class Sprite(pygame.sprite.Sprite):
    def __init__(self, image = None, rect = None):
        pygame.sprite.Sprite.__init__(self)
        if isinstance(image, basestring):
            image = rpg.resource.image(image)
        if image:
            self.image = image
        if rect:
            self.rect = Rect(rect)
        elif image:
            self.rect = image.get_rect()

    def sprites(self):
        return [self]

    def __setattr__(self, name, value):
        self.__dict__[name] = value
        if name == 'on_click':
            add_to_clickable(self.scene_group(), self)

    def __delattr__(self, name):
        if name == 'on_click':
            remove_from_clickable(self.scene_group(), self)
        del self.__dict__[name]

    def is_clicked(self):
        sg = self.scene_group()
        return sg.clickables.is_clicked(self) if sg else False

    def scene_group(self):
        for group in self.groups():
            sg = group.scene_group()
            if sg: return sg;
        return None

    def is_displayed(self):
        return not not self.scene_group()

class AnimationSprite(Sprite):

    def __init__(self, image, num_frame, position = (0, 0), fps = 6, repeat = True):
        pygame.sprite.Sprite.__init__(self)

        self.num_frame = num_frame
        self.fps = fps
        self.repeat = repeat
        self.current_frame = 0

        if isinstance(image, basestring):
            image = rpg.resource.image(image)
        self.images = splitSurface(image, num_frame)
        self.image = self.images[self.current_frame]
        self.rect = self.image.get_rect().move(position)

        self.start()

    def flip(self):
        self.images = [pygame.transform.flip(image, True, False) for image in self.images]
        self.image = self.images[self.current_frame]

    def stop(self):
        self.playing = False

    def start(self, on_finish_playing = None):
        self.playing = True
        self.last_frame_tick = pygame.time.get_ticks()

        if on_finish_playing:
            self.on_finish_playing = on_finish_playing

    def reset(self):
        self.stop()
        self.set_current_frame(0)

    def update(self):
        if not self.playing:
            return

        ms_per_frame = 1000.0 / self.fps
        proceed = (pygame.time.get_ticks() - self.last_frame_tick) / ms_per_frame
        if proceed >= 1:
            frame = self.current_frame + (int)(math.floor(proceed))
            if not self.repeat and frame >= self.num_frame:
                self.set_current_frame(self.num_frame - 1)
                self.stop()
                if (hasattr(self, 'on_finish_playing')):
                    self.on_finish_playing()
                    del self.on_finish_playing
            else:
                self.last_frame_tick += ms_per_frame * (frame - self.current_frame)
                self.set_current_frame(frame % self.num_frame)

    def set_current_frame(self, frame):
        self.current_frame = frame
        self.image = self.images[self.current_frame]

def splitSurface(surface, num):
    rect = surface.get_rect();
    area = pygame.Rect(0, 0, rect.width / num, rect.height)
    splitted = []
    for i in range(0, num):
        s = pygame.Surface(area.size)
        s.blit(surface, (0 , 0), area)
        s.set_colorkey(surface.get_at((0,0)), RLEACCEL)
        splitted.append(s.convert_alpha())
        area.move_ip(rect.width / num, 0)
    return splitted


class Translate(object):
    def __init__(self, sprite, from_pos, to_pos, duration, on_finish = rpg.lang.empty_function):
        self.sprite = sprite
        self.from_pos = from_pos
        self.to_pos = to_pos
        self.duration = duration
        self.on_finish = on_finish

        self.start_time = pygame.time.get_ticks()
        self._is_finished = False

        self.sprite_update = self.sprite.update
        self.sprite.update = self.update
        self.sprite.rect.topleft = self.from_pos

    def update(self):
        self.sprite_update()

        position = self.to_pos

        ratio = (float)(pygame.time.get_ticks() - self.start_time) / self.duration
        if ratio < 1:
            position = (
                (int)(self.from_pos[0] + (self.to_pos[0] - self.from_pos[0]) * ratio),
                (int)(self.from_pos[1] + (self.to_pos[1] - self.from_pos[1]) * ratio)
            )
        self.sprite.rect.topleft = position

        if ratio >= 1:
            self.sprite.update = self.sprite_update
            self._is_finished = True
            self.on_finish(rpg.event.Event(target = self))

    def is_finished(self):
        return self._is_finished
