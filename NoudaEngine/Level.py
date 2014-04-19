#!/usr/bin/python

import pygame
import GameObjects
import Globals
import Pathing
from Menu import *


## TODO: load all this shit from a file or something
## TODO: make a level controller class that loads levels and directs the state
class LevelBase():
	def __init__(self, level_id=None):
		self.LevelID = None
		self.GameOverMenu = SimpleMenu()
		self.GameOverMenu.set_title('Game Over')
		self.GameOverMenu.add_item(1, 'Return to main menu', self.m_goto_main)
		self.GameOverMenu.add_item(2, 'Exit', self.m_goto_exit)
		
	def m_goto_main(self):
		self.vars.UpperState = Globals.GameState.MENU
	
	def m_goto_exit(self):
		self.vars.Running = False
		
	def update(self):
		pass
	
	def draw(self, screen):
		pass

class LevelControl():
	def __init__(self):
		## Sorted list of LevelData() objects
		self.LoadedLevels = []
		self.CurrentLevel = None
		lvlone = LevelOne()
		self.load_level(lvlone)
	
	def load_level(self, levelObj):
		if isinstance(levolObj, LevelOne):
			self.LoadedLevels.append(levelObj)
			self.CurrentLevel = levelObj
		else:
			raise TypeError("Level is not correct type in load_level()!")

	def update(self):
		if self.CurrentLevel is not None:
			self.CurrentLevel.update()
	
	def draw(self, screen):
		if self.CurrentLevel is not None:
			self.CurrentLevel.draw(screen)

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
