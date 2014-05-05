#!/usr/bin/python

import pygame
import random
import math
import GameObjects
import Globals
import Pathing
import EventHandler
import Effects
from Menu import *
from Logger import *


class LevelState():
	MAINMENU = 0
	MENU = 1
	GAME = 2
	GAMEOVER = 3

## TODO: Level storage and loading.
class LevelBase():
	def __init__(self, level_id=None):
		self.LevelID = level_id
		self.KeyHandle = None
		self.JoyHandle = None
		self.Background = None
	
	def init_controls(self):
		raise NotImplementedError
	
	def update(self):
		raise NotImplementedError
	
	def draw(self, screen):
		raise NotImplementedError

class LevelControl():
	def __init__(self):
		## Sorted list of LevelData() objects
		self.LoadedLevels = []
		self.CurrentLevel = None
		self.LevelState = None
		
		self.MainMenu = SimpleMenu()
		self.MainMenu.set_title('Main Menu')
		self.MainMenu.add_item(10, 'Exit', self.m_exit)
		
		self.LevelMenu = SimpleMenu()
		self.LevelMenu.set_title('Paused')
		self.LevelMenu.add_item(1, 'Resume', self.m_resume)
		self.LevelMenu.add_item(2, 'Exit to main menu', self.show_main_menu)
		
		self.GameOverMenu = SimpleMenu()
		self.GameOverMenu.set_title('Game Over')
		self.GameOverMenu.add_item(1, 'Return to main menu', self.show_main_menu)
		self.GameOverMenu.add_item(2, 'Exit', self.m_exit)
		
		self.show_main_menu()
	
	def show_level_menu(self):
		self.LevelState = LevelState.MENU
		vars = Globals.Vars()
		vars.CurrentHandler = self.LevelMenu.KeyHandle
		vars.CurrentHandler_js = self.LevelMenu.JoyHandle
	
	def debug_dump(self):
		Debug(" == Dumping loaded levels ==")
		for l in self.LoadedLevels:
			Debug(str(l.LevelID))
		Debug(" == End Dump ==")
	
	def m_resume(self):
		self.LevelState = LevelState.GAME
		vars = Globals.Vars()
		vars.CurrentHandler = self.CurrentLevel.KeyHandle
		vars.CurrentHandler_js = self.CurrentLevel.JoyHandle
	
	def show_main_menu(self):
		self.LevelState = LevelState.MAINMENU
		vars = Globals.Vars()
		vars.CurrentHandler = self.MainMenu.KeyHandle
		vars.CurrentHandler_js = self.MainMenu.JoyHandle
		vars.CurrentHandler.add_keydown_handle(pygame.K_a, self.debug_dump)
	
	def m_exit(self):
		vars = Globals.Vars()
		vars.Running = False
	
	def start_level(self, levelid):
		Debug("Attempting to start level '" + str(levelid) + "'")
		vars = Globals.Vars()
		for l in self.LoadedLevels:
			if l.LevelID == levelid:
				self.CurrentLevel = l
				vars.CurrentHandler = l.KeyHandle
				vars.CurrentHandler_js = l.JoyHandle
				self.CurrentLevel.init_controls()
				self.CurrentLevel.KeyHandle.add_keydown_handle(pygame.K_ESCAPE, self.show_level_menu)
	
	def preload_level(self, levelObj):
		if isinstance(levelObj, LevelBase):
			self.LoadedLevels.append(levelObj)
			self.MainMenu.add_item(len(self.LoadedLevels) + 1, levelObj.LevelID, self.start_level, levelObj.LevelID)
			Debug("Loading level '" + str(levelObj.LevelID) + "'\n\tTotal loaded: " + str(len(self.LoadedLevels)))
		else:
			raise TypeError("Level is not correct type in load_level()!")

	def update(self):
		if self.LevelState is LevelState.MAINMENU:
			self.MainMenu.update()
		
		elif self.LevelState is LevelState.MENU:
			self.LevelMenu.update()
		
		elif self.LevelState is LevelState.GAME:
			if self.CurrentLevel is not None:
				self.CurrentLevel.update()
			else:
				raise RuntimeError("CurrentLevel is not set!")
		
		elif self.LevelState is LevelState.GAMEOVER:
			self.GameOverMenu.update()
	
	def draw(self, screen):
		if self.LevelState is LevelState.GAME:
			if self.CurrentLevel is not None:
				self.CurrentLevel.draw(screen)
			else:
				Warn("CurrentLevel is None! returning to the main menu.")
				self.LevelState = LevelState.MAINMENU
				self.MainMenu.draw(screen)
		
		elif self.LevelState is LevelState.MENU:
			self.LevelMenu.draw(screen)
		
		elif self.LevelState is LevelState.MAINMENU:
			self.MainMenu.draw(screen)
			
		elif self.LevelState is LevelState.GAMEOVER:
			self.GameOverMenu.draw(screen)
			
		else:
			raise NotImplementedError("Whoops.  From LevelControl.draw().")

class DefaultLevel(LevelBase):
	def __init__(self):
		LevelBase.__init__(self, 'Default Level')
		self.KeyHandle = EventHandler.KeyHandler("Default Level Handle")
		self.JoyHandle = EventHandler.JoyHandler("Default Level Joy Handle")

		## Actual level stuff now
		self.NextSpawn = 0
		self.Enemies = pygame.sprite.Group()
		self.Player = GameObjects.Player()
		self.Projectiles = pygame.sprite.Group()
		
		## Load the background and pre-calculate its dimensions
		vars = Globals.Vars()
		background = Globals.LoadImage('png/Backgrounds/purple.png')
		self.Background = pygame.Surface(vars.ScreenSize)
		widthRepeat = int(math.ceil(self.Background.get_width() / background.get_width()))
		heightRepeat = int(math.ceil(self.Background.get_height() / background.get_height()))
		
		## Tile the background image to fill the screen.
		(bgwidth, bgheight) = background.get_size()
		for h in range(0, heightRepeat + 1):
			for w in range(0, widthRepeat + 1):
				self.Background.blit(background, (w * bgwidth, h * bgheight))
		
		self.rand = random.Random()
		self.init_controls()

	def init_controls(self):
		self.KeyHandle.clear_all()
		self.KeyHandle.add_keyhold_handle(pygame.K_SPACE, self.Player.ToggleFire)
		self.KeyHandle.add_keyhold_handle(pygame.K_LEFT, self.Player.MoveLeft)
		self.KeyHandle.add_keyhold_handle(pygame.K_RIGHT, self.Player.MoveRight)
		self.KeyHandle.add_keyhold_handle(pygame.K_UP, self.Player.MoveUp)
		self.KeyHandle.add_keyhold_handle(pygame.K_DOWN, self.Player.MoveDown)
		self.KeyHandle.add_keydown_handle(pygame.K_b, self.Player.FireBomb)
		#self.KeyHandle.add_keydown_handle(pygame.K_a, self.JoyHandle.dump_hats)
		
		self.JoyHandle.clear_all()
		self.JoyHandle.add_joyhold_handle('hatposx', self.Player.MoveRight)
		self.JoyHandle.add_joyhold_handle('hatnegx', self.Player.MoveLeft)
		self.JoyHandle.add_joyhold_handle('hatposy', self.Player.MoveUp)
		self.JoyHandle.add_joyhold_handle('hatnegy', self.Player.MoveDown)
		self.JoyHandle.add_joyhold_handle(0, self.Player.ToggleFire)
		self.JoyHandle.add_joydown_handle(2, self.Player.FireBomb)
	
	def update(self):
		vars = Globals.Vars()
			
		if self.NextSpawn <= 0:
			x = self.rand.randint(vars.Bounds.left, vars.Bounds.right)
			y = 0

			mirror = False
			if x % 2 == 0:
				mirror = True

			e = GameObjects.Enemy()
			p = Pathing.MovementPath(e)
			p.load_path(Globals.FixPath('data/CurveDownPath.dat'), (x, y), 2, mirror)

			e.set_path(p)
			self.Enemies.add(e)
			self.NextSpawn = 60
		else:
			self.NextSpawn -= 1
		
		self.Enemies.update()
		self.Player.update()
		self.Projectiles.update()
		
		## TODO: projectile collision from non-player vehicles
		collisions = pygame.sprite.groupcollide(self.Enemies, self.Player.Projectiles, True, False)
		for sp in collisions:
			self.Projectiles.add(Effects.Explosion(Globals.UnitType.PLAYER, sp.rect.center))

	def draw(self, screen):
		screen.blit(self.Background, (0,0))
		self.Enemies.draw(screen)
		self.Player.draw(screen)
		self.Projectiles.draw(screen)