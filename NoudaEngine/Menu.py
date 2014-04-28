#!/usr/bin/python

## TODO: Make this functional (needs EventHandler tie-in)

import pygame
import math
import Globals
#import HeadsUpDisplay
import EventHandler
from Logger import *

__all__ = ["MenuItem", "MenuBase", "SimpleMenu"]

class MenuItem():
	def __init__(self, id, callback):
		self.ID = id
		self.Callback = callback
	
	def do_select(self):
		if self.Callback is not None:
			self.Callback()
		
	def update(self):
		pass
	
	def draw(self, screen):
		pass

class MenuBase():
	def __init__(self):
		self.vars = Globals.Vars()
		self.Font = pygame.font.Font(self.vars.DefaultFontPath, 25)
		self.FontColor = (255, 255, 255)
		self.Background = pygame.Surface(self.vars.ScreenSize)
		self.Background.fill((0, 0, 0))
		self.Dirty = True
		self._init_controls()
	
	def _init_controls(self):
		self.KeyHandle = EventHandler.KeyHandler("Menu Key Handler")
		self.JoyHandle = EventHandler.JoyHandler("Menu Joy Handler")

		## FIXME: Move this to some central place so we only do it once.  Maybe store the object in Globals?
		if pygame.joystick.get_count() > 0:
			js = pygame.joystick.Joystick(0)
			js.init()
			self.JoyHandle = EventHandler.JoyHandler(js, "Menu Joy Handler with " + js.get_name())

		# Shouldn't neet to clear_all(), but w/e
		self.KeyHandle.clear_all()
		self.KeyHandle.add_keydown_handle(pygame.K_DOWN, self.MoveDown)
		self.KeyHandle.add_keydown_handle(pygame.K_UP, self.MoveUp)
		self.KeyHandle.add_keydown_handle(pygame.K_RETURN, self.SelectItem)

		self.JoyHandle.clear_all()
		self.JoyHandle.add_joydown_handle('hatnegy', self.MoveDown)
		self.JoyHandle.add_joydown_handle('hatposy', self.MoveUp)
		self.JoyHandle.add_joydown_handle(0, self.SelectItem)

		self.vars.CurrentHandler_js = self.JoyHandle
		self.vars.CurrentHandler = self.KeyHandle


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
		def __init__(self, id, font, color, text, callback):
			MenuItem.__init__(self, id, callback)
			self.Text = text
			self.Color = (220, 202, 232)
			self.image = font.render(text, True, self.Color).convert_alpha()
			self.rect = self.image.get_rect()
			
	def __init__(self):
		MenuBase.__init__(self)
		#self.vars = Globals.Vars()
		#self.Font = pygame.font.Font("profont.ttf", 25)
		#self.FontColor = (255, 255, 255)
		self.MenuItems = []
		
		Debug("ScreenSize: " + str(self.vars.ScreenSize))

		#self.background = pygame.Surface(self.vars.ScreenSize)
		#self.Dirty = True
		
		self.GameBackground = None
		
		#self.background.fill((0, 0, 0))
		self.Background.set_alpha(127)
		
		self.ItemsWidth = 0
		self.ItemsHeight = 0
		self.ItemPadding = 10
		
		self.Cursor = pygame.transform.rotate(Globals.LoadImage('png/UI/playerLife1_red.png'), -90)
		self.CurrentSelection = -1
		self.Title = None
		
		"""self.Handler = EventHandler.KeyHandler("Simple Menu Handler")
		self.Handler.add_keydown_handle(pygame.K_DOWN, self.MoveDown)
		self.Handler.add_keydown_handle(pygame.K_UP, self.MoveUp)
		self.Handler.add_keydown_handle(pygame.K_RETURN, self.SelectItem)"""
	
	def set_background(self, screen):
		self.GameBackground = screen
	
	def set_title(self, text):
		titlefont = pygame.font.Font(self.vars.DefaultFontPath, 40)
		self.Title = titlefont.render(text, True, self.FontColor).convert_alpha()
	
	def add_item(self, id, text, callback=None):
		self.MenuItems.append(SimpleMenu.SimpleMenuItem(id, self.Font, self.FontColor, text, callback))
		if len(self.MenuItems) >= 1:
			self.CurrentSelection = 0
		
		for i in self.MenuItems:
			if self.ItemsWidth < i.image.get_width():
				self.ItemsWidth = i.image.get_width()
			self.ItemsHeight += i.image.get_height() + self.ItemPadding
		
	def draw(self, surface):
		MenuBase.draw(self, surface)
		
		startx = self.Background.get_rect().centerx - self.ItemsWidth / 2
		starty = self.Background.get_rect().centery - self.ItemsHeight / 2
		
		if self.GameBackground is not None:
			surface.blit(self.GameBackground, (0, 0))
		surface.blit(self.Background, (0, 0))
		
		if self.Title is not None:
			surface.blit(self.Title, ((self.vars.Bounds.centerx - (self.Title.get_width() / 2.0)), 100))
		
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
			print "Tried to select a menu item where none exist!"
			return
		elif self.CurrentSelection >= len(self.MenuItems):
			print "Tried to select a menu item past the last item!"
			return
		
		self.MenuItems[self.CurrentSelection].do_select()			
	
	def update(self):
		pass
	
