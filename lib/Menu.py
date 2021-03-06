#!/usr/bin/python

## TODO: Make this functional (needs EventHandler tie-in)

import pygame
import math
from lib.Globals import Vars, LoadImage, TileImage
from lib.EventHandler import KeyHandler, JoyHandler
from lib.Logger import *

__all__ = ["MenuItem", "MenuBase", "SimpleMenu"]

class MenuItem():
    def __init__(self, weight, callback, args):
        self.Weight = weight
        self.Callback = callback
        self.Args = args

    def do_select(self):
        if self.Callback is not None:
            if self.Args is not None:
                self.Callback(self.Args)
            else:
                self.Callback()

    def update(self):
        raise NotImplementedError

    def draw(self, screen):
        raise NotImplementedError

class MenuBase():
    def __init__(self):
        self.vars = Vars()
        self.Font = pygame.font.Font(self.vars.DefaultFontPath, 25)
        self.FontColor = (255, 255, 255)
        self.Background = pygame.Surface(pygame.display.get_surface().get_size())
        self.Background.fill((0, 0, 0))
        self.Dirty = True
        self._init_controls()

    def _init_controls(self):
        self.KeyHandle = KeyHandler("Menu Key Handler")
        self.JoyHandle = JoyHandler("Menu Joy Handler")

        # Shouldn't neet to clear_all(), but w/e
        self.KeyHandle.clear_all()
        self.KeyHandle.add_keydown_handle(pygame.K_DOWN, self.MoveDown)
        self.KeyHandle.add_keydown_handle(pygame.K_UP, self.MoveUp)
        self.KeyHandle.add_keydown_handle(pygame.K_RETURN, self.SelectItem)

        ## These are configured for a GameCube controller.  It's all I have right now...
        self.JoyHandle.clear_all()
        self.JoyHandle.add_joydown_handle('hatnegy', self.MoveDown)
        self.JoyHandle.add_joydown_handle('hatposy', self.MoveUp)
        self.JoyHandle.add_joydown_handle(1, self.SelectItem)
        self.JoyHandle.add_joydown_handle('a1pos', self.MoveDown)
        self.JoyHandle.add_joydown_handle('a1neg', self.MoveUp)

    def reset(self):
        raise NotImplementedError

    def DoSelect(self):
        raise NotImplementedError

    def MoveDown(self):
        raise NotImplementedError

    def MoveUp(self):
        raise NotImplementedError

    def MoveLeft(self):
        raise NotImplementedError

    def MoveRight(self):
        raise NotImplementedError

    def update(self):
        raise NotImplementedError

    def draw(self, surface):
        if not self.Dirty:
            return
        self.Dirty = False

class SimpleMenu(MenuBase):
    class SimpleMenuItem(MenuItem):
        def __init__(self, weight, font, color, text, callback, args):
            MenuItem.__init__(self, weight, callback, args)
            self.Text = text
            self.Color = (220, 202, 232)
            self.image = font.render(text, True, self.Color).convert_alpha()
            self.rect = self.image.get_rect()

    def __init__(self):
        MenuBase.__init__(self)
        self.MenuItems = []
        self.GameBackground = None
        self.Background.set_alpha(127)

        self.ItemsWidth = 0
        self.ItemsHeight = 0
        self.ItemPadding = 10

        self.Cursor = pygame.transform.rotate(LoadImage('png/UI/playerLife1_red.png'), -90)
        self.CurrentSelection = -1
        self.Title = None

        self.set_background(TileImage('png/Backgrounds/blue.png'))

    def reset(self):
        if len(self.MenuItems) > 0:
            self.CurrentSelection = 0
        else:
            self.CurrentSelection = -1

    def set_background(self, screen):
        self.GameBackground = screen

    def set_title(self, text):
        titlefont = pygame.font.Font(self.vars.DefaultFontPath, 40)
        self.Title = titlefont.render(text, True, self.FontColor).convert_alpha()

    def add_item(self, weight, text, callback=None, args=None):
        self.MenuItems.append(SimpleMenu.SimpleMenuItem(weight, self.Font, self.FontColor, text, callback, args))
        if len(self.MenuItems) >= 1:
            self.CurrentSelection = 0

        for i in self.MenuItems:
            if self.ItemsWidth < i.image.get_width():
                self.ItemsWidth = i.image.get_width()
            self.ItemsHeight += i.image.get_height() + self.ItemPadding

        # Sort the menu items by weight
        self.MenuItems = sorted(self.MenuItems, key=lambda item: item.Weight)

    def draw(self, surface):
        #MenuBase.draw(self, surface)

        startx = self.Background.get_rect().centerx - self.ItemsWidth / 2
        starty = self.Background.get_rect().centery - self.ItemsHeight / 2

        if self.GameBackground is not None:
            surface.blit(self.GameBackground, (0, 0))
        else:
            self.Background.set_alpha(255)

        surface.blit(self.Background, (0, 0))

        if self.Title is not None:
            surface.blit(self.Title, ((pygame.display.get_surface().get_rect().centerx - (self.Title.get_width() / 2.0)), 100))

        num = 0
        for i in self.MenuItems:
            x = (self.ItemsWidth / 2 - i.rect.width / 2 + startx)
            y = (num * (i.rect.height + self.ItemPadding) + starty)
            surface.blit(i.image, (x, y))

            if self.CurrentSelection > -1 and self.CurrentSelection == num:
                surface.blit(self.Cursor, (surface.get_rect().centerx - (self.ItemsWidth / 2) - 50, y))
            num += 1

    def MoveDown(self):
        self.Dirty = True
        lastidx = len(self.MenuItems) - 1
        if self.CurrentSelection >= lastidx:
            return

        self.CurrentSelection += 1

    def MoveUp(self):
        self.Dirty = True
        if self.CurrentSelection <= 0:
            return

        self.CurrentSelection -= 1

    def MoveLeft(self):
        pass

    def MoveRight(self):
        pass

    def DoSelect(self):
        self.SelectItem()

    def SelectItem(self):
        if self.CurrentSelection < 0:
            print("Tried to select a menu item where none exist!")
            return
        elif self.CurrentSelection >= len(self.MenuItems):
            print("Tried to select a menu item past the last item!")
            return

        self.MenuItems[self.CurrentSelection].do_select()

    def update(self):
        pass

