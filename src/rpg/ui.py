# -*- coding:utf-8 -*-

import math
import pygame
from rpg.constants import *
import rpg.sprite
import rpg.resource
import rpg.event
import rpg.draw

class CursorSprite(rpg.sprite.Sprite):

    def __init__(self, margin = 10, position = 'left'):
        rpg.sprite.Sprite.__init__(self, 'cursor.png')
        self.margin = margin
        self.position = position
        if self.position == 'right':
            self.image = pygame.transform.flip(self.image, True, False)

    def point(self, sprite):
        if self.position == 'left':
            self.rect.midright = sprite.rect.midleft
            self.rect.move_ip(- self.margin, 0)
        elif self.position == 'right':
            self.rect.midleft = sprite.rect.midright
            self.rect.move_ip(self.margin, 0)

class RadioGroup(rpg.sprite.Group):
    def __init__(self, *buttons):
        self._buttons = []
        rpg.sprite.Group.__init__(self)
        self.add(*buttons)

        self.selected_button = None
        self.focused_button = None

    def add(self, *buttons):
        rpg.sprite.Group.add(self, *buttons)
        for button in buttons:
            if isinstance(button, RadioButton):
                self._buttons.append(button)
                button.radio_group = self

    def empty(self):
        "dont use remove(sprite), instead use empty()"
        rpg.sprite.Group.empty(self)
        self._buttons = []
        self.selected_button = None
        self.focused_button = None

    def buttons(self):
        return self._buttons

    def select(self, button, by_mouse = False, silence = False):
        #if self.selected_button == button: return

        if not button.enabled: return

        if self.selected_button != button:
            if self.selected_button:
                self.selected_button.unselect()

            button.select()
            self.selected_button = button

        if not silence:
            self.invoke_event('select', button = button, by_mouse = by_mouse)

    def select_for(self, item, by_mouse = False, silence = False):
        button = self.button_for(item)
        if button: self.select(button, by_mouse, silence)

    def focus(self, button):
        if self.focused_button == button: return

        self.unfocus()

        button.focus()
        self.focused_button = button

        self.invoke_event('focus', button = button)

    def unfocus(self, button = None):
        if not button:
            button = self.focused_button

        if not self.focused_button or self.focused_button != button: return
        self.focused_button.unfocus()
        self.focused_button = None

        self.invoke_event('unfocus', button = button)

    def button_for(self, item):
        for button in self.buttons():
            if button.item == item: return button
        return None

    def button_distance_from(self, button, increment, loop = True):
        index = self.buttons().index(button) + increment
        if not loop and not (0 <= index < len(self.buttons())): return None
        return self.buttons()[index % len(self.buttons())];

    def next_button(self, button, loop = True):
        return self.button_distance_from(button, 1, loop)

    def prev_button(self, button, loop = True):
        return self.button_distance_from(button, -1, loop)

    def focused_or_selected_button(self):
        return self.focused_button or self.selected_button


    def invoke_event(self, event_name, **kwargs):
        handler_name = 'on_' + event_name
        if hasattr(self, handler_name):
            getattr(self, handler_name)(rpg.event.Event(target = self, **kwargs))


class RadioTable(RadioGroup):
    def __init__(self, cols, *buttons):
        RadioGroup.__init__(self, *buttons)
        self.cols = cols
        self.margin = (16, 2)

    def add(self, *buttons):
        old_length = len(self.buttons())
        RadioGroup.add(self, *buttons)
        for i, button in enumerate(buttons):
            self.align(old_length + i, button)

    def align(self, index, button):
        origin = self.buttons()[0].rect.topleft if len(self.buttons()) > 0 else button.rect.topleft
        button.rect.topleft = (
            origin[0] + (button.rect.width + self.margin[0]) * (index % self.cols),
            origin[1] + (button.rect.height + self.margin[1]) * math.floor(index / self.cols)
        )

    def up_button(self, button, loop = True):
        index = self.buttons().index(button) - self.cols
        if index < 0:
            if loop:
                while index < len(self.buttons()):
                    index += self.cols
                else:
                    index -= self.cols
            else:
                index += self.cols
        return self.buttons()[index]

    def down_button(self, button, loop = True):
        index = self.buttons().index(button) + self.cols
        if index >= len(self.buttons()):
            if loop:
                while index >= 0:
                    index -= self.cols
                else:
                    index += self.cols
            else:
                index -= self.cols
        return self.buttons()[index]

    def left_button(self, button, loop = True):
        index = self.buttons().index(button) - 1
        if (index + 1) % self.cols == 0:
            if loop:
                index = min([index + self.cols, len(self.buttons()) - 1])
            else:
                index += 1
        return self.buttons()[index]

    def right_button(self, button, loop = True):
        index = self.buttons().index(button) + 1
        if index >= len(self.buttons()) or index % self.cols == 0:
            if loop:
                index -= 1
                index -= index % self.cols
            else:
                index -= 1
        return self.buttons()[index]
    

class RadioButton(rpg.sprite.Sprite):
    def __init__(self, label, rect, item = None, enabled = True):
        rpg.sprite.Sprite.__init__(self, pygame.Surface(rect.size), rect)
        self.label = label
        self.item = item
        self.enabled = enabled
        self.radio_group = None
        self.selected = False
        self.focused = False
        self.draw_image()

    def select(self):
        self.selected = True
        self.draw_image()

    def unselect(self):
        self.selected = False
        self.draw_image()

    def focus(self):
        self.focused = True
        self.draw_image()

    def unfocus(self):
        self.focused = False
        self.draw_image()

    def on_click(self, event):
        if not self.enabled: return
        if event.button == MOUSE_BUTTON_LEFT:
            self.radio_group.select(self, by_mouse = True)

    def on_mouse_over(self, event):
        self.radio_group.focus(self)

    def on_mouse_out(self, event):
        self.radio_group.unfocus(self)

    def draw_image(self):
        self.image.fill((255, 255, 255))

        if self.selected or self.focused:
            border_color = (0, 0, 0) if self.selected else COLOR_DISABLED
            rpg.draw.rounded_rect(self.image, self.image.get_rect().inflate(-2, -2), border_color = border_color)

        label_color = (0, 0, 0) if self.enabled else COLOR_DISABLED
        label_image = rpg.resource.font().render(self.label, False, label_color)
        self.image.blit(label_image, (5, (self.rect.height - label_image.get_rect().height) / 2))


class ToggleTable(RadioTable):
    def select(self, button, by_mouse = False, silence = False):
        if not button.enabled: return
        button.select()
        if not silence:
            self.invoke_event('select', button = button, by_mouse = by_mouse)

    def unselect(self, button, by_mouse = False, silence = False):
        if not button.enabled: return
        button.unselect()
        if not silence:
            self.invoke_event('unselect', button = button, by_mouse = by_mouse)

    def toggle(self, button, by_mouse = False, silence = False):
        if button.selected:
            self.unselect(button, by_mouse, silence)
        else:
            self.select(button, by_mouse, silence)

class ToggleButton(RadioButton):
    def on_click(self, event):
        if not self.enabled: return
        if event.button == MOUSE_BUTTON_LEFT:
            self.radio_group.toggle(self, by_mouse = True)
