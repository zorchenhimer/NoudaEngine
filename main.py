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

import NoudaEngine.LevelAsteroids

from NoudaEngine.Logger import *
from NoudaEngine.Globals import FixPath

## FIXME: sticky keys when you enter the menu with a keyhold event active

class GameEngine():
	def __init__(self, w=1280, h=720, cap=60):
		SetPrintLevel(LogLevel.DEBUG)
		SetLogLevel(LogLevel.DEBUG)
		Info("Starting init...")
		self.vars = NoudaEngine.Globals.Vars()
		self.width, self.height = [w, h]
		os.environ['SDL_VIDEO_CENTERED'] = '1'
		
		pygame.display.set_caption('NoudaEngine')
		self.screen = pygame.display.set_mode((self.width, self.height))#, pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)
		Debug("Creating screen with dimensions " + str((w, h)))
		pygame.init()
		pygame.joystick.init()
		
		icosurf = pygame.Surface((33,26))
		icokey = pygame.Color(0,0,0)
		icosurf.fill(icokey)
		icosurf.blit(NoudaEngine.Globals.LoadImage('png/UI/playerLife1_red.png'), (0,0))
		icosurf.set_colorkey(icokey)
		pygame.display.set_icon(icosurf)
		
		self.tps = cap
		Debug("Ticks per second cap: " + str(self.tps))
		self.clock = pygame.time.Clock()		## Might want to move this to Globals.Vars() for physics or frame-independent timing
		self.hud = NoudaEngine.HeadsUpDisplay.HUD(self.screen.get_size())
		Debug(str(self.screen.get_size()))
		
		self.vars.Bounds = self.screen.get_rect()
		self.vars.ScreenSize = self.screen.get_size()
		self.vars.LevelControl = NoudaEngine.Level.LevelControl()

		self.vars.LevelControl.preload_level(NoudaEngine.Level.DefaultLevel())
		self.vars.LevelControl.preload_level(NoudaEngine.LevelAsteroids.Asteroids())
		
		Info("Init finished.")
		
		self.start_game()
		
	def start_game(self):
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
					if event.key is pygame.K_F12 or event.key is pygame.K_s:
						pygame.image.save(self.screen, 'screenshot.png')
						Info('Screenshot saved.')
					if event.key is pygame.K_z:
						Debug("CurrentHandler: " + self.vars.CurrentHandler.Name + " [" + str(self.vars.CurrentHandler.randID) + "]")
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
			
			#if self.vars.UpperState == NoudaEngine.Globals.GameState.GAME or firstloop:
			self.vars.LevelControl.update()
			
			## Draw stuff
			self.vars.LevelControl.draw(self.screen)

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
