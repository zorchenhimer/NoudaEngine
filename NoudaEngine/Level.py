#!/usr/bin/python

import pygame
import GameObjects
import Globals
import Pathing
import EventHandler
import Effects
import random
from Menu import *
from Logger import *


class LevelState():
	MENU = 1
	GAME = 2
	GAMEOVER = 3

## TODO: load all this shit from a file or something
## TODO: make a level controller class that loads levels and directs the state
class LevelBase():
	def __init__(self, level_id=None):
		self.LevelID = None
		self.KeyHandle = None
		self.JoyHandle = None
		
	def update(self):
		pass
	
	def draw(self, screen):
		pass

class LevelControl():
	def __init__(self):
		## Sorted list of LevelData() objects
		self.LoadedLevels = []
		self.CurrentLevel = None
		self.KeyHandle = None
		self.JoyHandle = None
		self.LevelState = LevelState.GAME
		
		lvlone = DefaultLevel()
		self.preload_level(lvlone)
		
		self.KeyHandle.add_keydown_handle(pygame.K_ESCAPE, self.show_menu)
		
		self.LevelMenu = SimpleMenu()
		self.LevelMenu.set_title('Paused')
		self.LevelMenu.add_item(1, 'Resume', self.m_resume)
		self.LevelMenu.add_item(2, 'Exit to main menu', self.m_exit_to_main)
		
		self.GameOverMenu = SimpleMenu()
		self.GameOverMenu.set_title('Game Over')
		self.GameOverMenu.add_item(1, 'Return to main menu', self.m_exit_to_main)
		self.GameOverMenu.add_item(2, 'Exit', self.m_exit)
		
		#vars = Globals.Vars()
		#vars.CurrentHandler = self.KeyHandle
		#vars.CurrentHandler_js = self.JoyHandle
	
	def show_menu(self):
		self.LevelState = LevelState.MENU
		vars = Globals.Vars()
		vars.CurrentHandler = self.LevelMenu.KeyHandle
		vars.CurrentHandler_js = self.LevelMenu.JoyHandle
	
	def m_resume(self):
		self.LevelState = LevelState.GAME
		vars = Globals.Vars()
		vars.CurrentHandler = self.KeyHandle
		vars.CurrentHandler_js = self.JoyHandle
	
	def m_exit_to_main(self):
		self.m_resume()
		vars = Globals.Vars()
		vars.UpperState = Globals.GameState.MENU
		vars.CurrentHandler = vars.MainMenu.KeyHandle
		vars.CurrentHandler_js = vars.MainMenu.JoyHandle

	
	def m_exit(self):
		vars = Globals.Vars()
		vars.Running = False
	
	def preload_level(self, levelObj):
		if isinstance(levelObj, LevelBase):
			self.LoadedLevels.append(levelObj)
			self.CurrentLevel = levelObj
			self.KeyHandle = self.CurrentLevel.KeyHandle
			self.JoyHandle = self.CurrentLevel.JoyHandle
		else:
			raise TypeError("Level is not correct type in load_level()!")

	def update(self):
		if self.CurrentLevel is not None:
			self.CurrentLevel.update()
	
	def draw(self, screen):
		if self.LevelState is LevelState.GAME:
			if self.CurrentLevel is not None:
				self.CurrentLevel.draw(screen)
		elif self.LevelState is LevelState.MENU:
			self.LevelMenu.draw(screen)
		elif self.LevelState is LevelState.GAMEOVER:
			pass
		else:
			raise NotImplementedError("Whoops.  From LevelControl.draw().")

class DefaultLevel(LevelBase):
	def __init__(self):
		self.KeyHandle = EventHandler.KeyHandler("Default Level Handle")
		self.JoyHandle = EventHandler.JoyHandler("Default Level Joy Handle")

		## Actual level stuff now
		self.NextSpawn = 0
		self.Enemies = pygame.sprite.Group()
		self.Player = GameObjects.Player()
		self.Projectiles = pygame.sprite.Group()
		
		self.rand = random.Random()
		
		self.InitControls()

	def InitControls(self):
		self.KeyHandle.clear_all()
		self.KeyHandle.add_keyhold_handle(pygame.K_SPACE, self.Player.ToggleFire)
		self.KeyHandle.add_keyhold_handle(pygame.K_LEFT, self.Player.MoveLeft)
		self.KeyHandle.add_keyhold_handle(pygame.K_RIGHT, self.Player.MoveRight)
		self.KeyHandle.add_keyhold_handle(pygame.K_UP, self.Player.MoveUp)
		self.KeyHandle.add_keyhold_handle(pygame.K_DOWN, self.Player.MoveDown)
		self.KeyHandle.add_keydown_handle(pygame.K_b, self.Player.FireBomb)
		
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
		self.Enemies.draw(screen)
		self.Player.draw(screen)
		self.Projectiles.draw(screen)

"""		
## FIXME: Move this somewhere else once it starts working
class LevelOne(LevelBase):
	class lvlEnemy(GameObjects.Enemy):
		## TODO: add some AI or something...
		def __init__(self):
			GameObjects.Enemy.__init__(self)
			self.firing = True
			self.path = Pathing.MovementPath()
			self.path.add_waypoint(Pathing.MovementPath.Mode.DANCE, (20, 20), 0)
			self.path.add_waypoint(Pathing.MovementPath.Mode.DANCE, (700, 20), 200)
			self.path.add_waypoint(Pathing.MovementPath.Mode.DANCE, (20, 20), 400)

		def draw(self, screen):
			screen.blit(self.image, self.rect)
	
	class lvlOneStates():
		GAME = 1
		MENU = 2

	def __init__(self):
		self.vars = Globals.Vars()
		self.GameOverMenu = SimpleMenu()
		self.Player = self.vars.Player()
		self.Enemy = lvlEnemy()

		self.GameOverMenu.set_title("Game Over")
		self.GameOverMenu.add_item(1, "Return To Main", self.m_return_to_main)
		self.GameOverMune.add_item(2, "Exit", self.m_exit)
		
		self.CurrentState = lvlOneStates.GAME

		if self.Player is None:
			self.Player = GameObjects.Player()
	
	def set_bindings(self):
		pass

	def update(self):
		self.Enemy.update()
		self.Player.update()

		if self.Enemy is None:
			pass	#Gameover
	
	def m_exit(self):
		self.vars.Running = False

	def m_return_to_main(self):
		pass
"""