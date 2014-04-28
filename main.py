#!/usr/bin/python

import pygame
import os
import time
import math
import random

import NoudaEngine.EventHandler
import NoudaEngine.Globals
import NoudaEngine.GameObjects
import NoudaEngine.HeadsUpDisplay
import NoudaEngine.Menu
import NoudaEngine.Level
import NoudaEngine.Pathing
import NoudaEngine.Logger

from NoudaEngine.Logger import *
from NoudaEngine.Globals import FixPath

####
## TODO: try using dirty sprites to speed things up on the pi

## FIXME: sticky keys when you enter the menu with a keyhold event active

class GameEngine():
	def __init__(self, w=1280, h=720, cap=60):
		SetPrintLevel(LogLevel.DEBUG)
		SetLogLevel(LogLevel.DEBUG)
		Info("Starting init...")
		self.vars = NoudaEngine.Globals.Vars()
		self.width, self.height = [w, h]
		self.screen = pygame.display.set_mode((self.width, self.height))#, pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)
		Debug("Creating screen with dimensions " + str((w, h)))
		os.environ['SDL_VIDEO_CENTERED'] = '1'	## FIXME: THIS SHIT DON'T WORK
		pygame.init()
		pygame.joystick.init()
		
		self.GameHandler = NoudaEngine.EventHandler.KeyHandler("Main Game Handler")
		self.MenuHandler = NoudaEngine.EventHandler.KeyHandler("Main Menu Handler")
		
		if pygame.joystick.get_count() > 0:
			js = pygame.joystick.Joystick(0)
			js.init()
			self.GameHandler_js = NoudaEngine.EventHandler.JoyHandler(js, "Game Handler with " + js.get_name())
			self.MenuHandler_js = NoudaEngine.EventHandler.JoyHandler(js, "Menu Handler with " + js.get_name())
			self.vars.CurrentHandler_js = self.MenuHandler_js
		else:
			self.GameHandler_js = NoudaEngine.EventHandler.DummyJoy(None, "No Joy Found")
			self.MenuHandler_js = self.GameHandler_js
			self.vars.CurrentHandler_js = self.MenuHandler_js
			
		self.tps = cap
		Debug("Ticks per second cap: " + str(self.tps))
		self.clock = pygame.time.Clock()		## Might want to move this to Globals.Vars() for physics or frame-independent timing
		self.hud = NoudaEngine.HeadsUpDisplay.HUD(self.screen.get_size())
		
		## Load the background and pre-calculate its dimensions
		background = NoudaEngine.Globals.LoadImage('png/Backgrounds/purple.png')
		self.sizedBackground = pygame.Surface(self.screen.get_size())
		Debug(str(self.screen.get_size()))
		widthRepeat = int(math.ceil(self.sizedBackground.get_width() / background.get_width()))
		heightRepeat = int(math.ceil(self.sizedBackground.get_height() / background.get_height()))
		
		## Tile the background image to fill the screen.
		(bgwidth, bgheight) = background.get_size()
		for h in range(0, heightRepeat + 1):
			for w in range(0, widthRepeat + 1):
				self.sizedBackground.blit(background, (w * bgwidth, h * bgheight))
		
		## Bounds border in pixels
		border = 30
		
		## Calculate the bounding box
		bounds = self.screen.get_rect()
		bounds.top += border
		bounds.left += border
		bounds.width -= border * 2
		bounds.height -= border * 2
		
		## Make the bounding box visible
		pygame.draw.rect(self.sizedBackground, pygame.Color(0, 0, 0), bounds, 1)
		
		self.vars.Bounds = bounds
		self.vars.ScreenSize = self.screen.get_size()
		
		#self.vars.Player = NoudaEngine.GameObjects.Player()
		
		self.Menu = NoudaEngine.Menu.SimpleMenu()
		self.Menu.set_title('Main Menu')
		self.Menu.add_item(1, 'Start Game', self.m_start_game)
		self.Menu.add_item(2, 'Exit', self.m_exit_game)
		
		self.vars.CurrentHandler = self.Menu.KeyHandle
		self.vars.CurrentHandler_js = self.Menu.JoyHandle
		
		self.vars.CurrentLevel = NoudaEngine.Level.DefaultLevel()

		#pygame.mouse.set_visible(False)
		Info("Init finished.")
	
	def m_start_game(self):
		Info("'Start Game' menu item selected.  Starting game.")
		self.vars.UpperState = NoudaEngine.Globals.GameState.GAME
		self.vars.CurrentHandler = self.GameHandler
		self.vars.CurrentHandler_js = self.GameHandler_js
	
	def m_exit_game(self):
		Info("'Exit Game' menu item selected.  Exiting.")
		self.vars.Running = False
		
	def show_menu(self):
		self.vars.UpperState = NoudaEngine.Globals.GameState.MENU
		self.vars.Player.StopFire()
		self.vars.CurrentHandler = self.Menu.KeyHandle
		self.vars.CurrentHandler_js = self.Menu.JoyHandle
		
		self.Menu.Dirty = True
		self.Menu.update()
		
		## Set this here so we don't have to re-draw all of the sprites each
		## tick wen the menu is active.
		self.Menu.set_background(self.screen.copy())
	
	def set_ingame_bindings(self):
		## TODO: move this stuff to the level and menu code, respectively.
		
		## Normal game state
		self.GameHandler.clear_all()
		self.GameHandler.add_keyhold_handle(pygame.K_SPACE, self.vars.Player.ToggleFire)
		self.GameHandler.add_keyhold_handle(pygame.K_LEFT, self.vars.Player.MoveLeft)
		self.GameHandler.add_keyhold_handle(pygame.K_RIGHT, self.vars.Player.MoveRight)
		self.GameHandler.add_keyhold_handle(pygame.K_UP, self.vars.Player.MoveUp)
		self.GameHandler.add_keyhold_handle(pygame.K_DOWN, self.vars.Player.MoveDown)
		self.GameHandler.add_keydown_handle(pygame.K_b, self.vars.Player.FireBomb)
		self.GameHandler.add_keydown_handle(pygame.K_ESCAPE, self.show_menu)
		
		self.GameHandler_js.clear_all()
		self.GameHandler_js.add_joyhold_handle('hatposx', self.vars.Player.MoveRight)
		self.GameHandler_js.add_joyhold_handle('hatnegx', self.vars.Player.MoveLeft)
		self.GameHandler_js.add_joyhold_handle('hatposy', self.vars.Player.MoveUp)
		self.GameHandler_js.add_joyhold_handle('hatnegy', self.vars.Player.MoveDown)
		self.GameHandler_js.add_joyhold_handle(0, self.vars.Player.ToggleFire)
		self.GameHandler_js.add_joydown_handle(2, self.vars.Player.FireBomb)
		self.GameHandler_js.add_joydown_handle(7, self.show_menu)
	
	def start_game(self):
		self.set_ingame_bindings()
		running = True
		
		nextspawn = 0
		firstloop = True
		rand = random.Random()
		
		while self.vars.Running:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					self.vars.Running = False
					break
				if event.type == pygame.KEYDOWN:
					self.vars.CurrentHandler.do_keydown(event.key)
				if event.type == pygame.KEYUP:
					self.vars.CurrentHandler.do_keyup(event.key)
				if event.type == pygame.JOYBUTTONDOWN:
					self.vars.CurrentHandler_js.do_joydown(event.button, event.joy)
				if event.type == pygame.JOYBUTTONUP:
					self.vars.CurrentHandler_js.do_joyup(event.button, event.joy)
			
			self.vars.CurrentHandler_js.update()
			
			if self.vars.Running == False:
				continue
			
			if self.vars.UpperState == NoudaEngine.Globals.GameState.GAME or firstloop:
				## Update the sprite groups.
				self.vars.GameEnemies.update()
				self.vars.GameProjectiles.update()
				self.vars.Player.update()
				if nextspawn <= 0:
					x = rand.randint(self.vars.Bounds.left, self.vars.Bounds.right)
					y = 0
					#Debug("offset: (" + str(x) + ', ' + str(y) + ')')
					
					mirror = False
					if(x % 2 == 0):
						mirror = True
						
					e = NoudaEngine.GameObjects.Enemy()
					p = NoudaEngine.Pathing.MovementPath(e)
					p.load_path(FixPath('data/CurveDownPath.dat'), (rand.randint(self.vars.Bounds.left, self.vars.Bounds.right), 0), 2, mirror)
					
					e.set_path(p)
					self.vars.GameEnemies.add(e)
					nextspawn = 60
				else:
					nextspawn -= 1
			
			## Draw stuff
			if self.vars.UpperState == NoudaEngine.Globals.GameState.MENU:
				## Draw the menu.
				if firstloop:
					## Grab the screen before the menu is displayed so we can
					## display it as the background without redrawing everything
					## every frame.
					self.screen.blit(self.sizedBackground, (0, 0))
					self.vars.Player.draw(self.screen)
					self.show_menu()
					firstloop = False
				self.Menu.draw(self.screen)
				
			elif self.vars.UpperState == NoudaEngine.Globals.GameState.GAME:
				## Draw the game field sprites.
				self.screen.blit(self.sizedBackground, (0,0))
				self.vars.Player.draw(self.screen)
				self.vars.GameEnemies.draw(self.screen)
				self.vars.GameProjectiles.draw(self.screen)

			self.hud.set_text(NoudaEngine.HeadsUpDisplay.Locations.TOPRIGHT, str(math.floor(self.clock.get_fps())))
			
			## Draw the hud, then update the display.
			self.hud.blit_to_surface(self.screen)
			pygame.display.flip()
			self.clock.tick(self.tps)

		else:
			pygame.joystick.quit()
			pygame.quit()
			exit()
	
if __name__ == "__main__":
	game = GameEngine(1360, 768)
	game.start_game()
