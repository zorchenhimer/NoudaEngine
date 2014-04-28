#!/usr/bin/python

## Holds variables and objects that are needed by a bunch of different classes

import pygame
import platform
import os.path as path
#import NoudaEngine.Logger.Debug as Debug
#from Logger import Debug, Warn, Info

class UnitType():
	PLAYER = 1
	ENEMY = 2

class GameState():
	""" Top level game states. """
	MENU = 1
	GAME = 2
	GAMEOVER = 3

def LoadImage(path):
	""" Return a surface containing the image at the given path. """
	surf = None
	try:
		surf = pygame.Surface.convert_alpha(pygame.image.load(path))
	except Exception as exc:
		print("Unable to load image at path '" + path + "': " + str(exc))
	return surf

def GTFO():
	""" FUCK THIS SHIT """
	print "FUCK THIS SHIT"
	pygame.quit()
	exit()

def FixPath(p):
	""" Return the correct path format depending on the current system. """
	if platform.system().lower() == 'windows':
		return path.abspath(p.replace('/', '\\'))
	else:
		return path.abspath(p.replace('\\', '/'))

class Vars():
	## Actual class here.
	class _vars:
		def __init__(self):
			self.Bounds = None
			self.Paused = False
			self.gameSprites = pygame.sprite.LayeredUpdates()#Group()
			self.GameProjectiles = pygame.sprite.Group()
			self.GameEnemies = pygame.sprite.Group()
			self.Player = None
			self.UpperState = GameState.MENU
			self.Running = True
			self.DefaultFontPath = "NoudaEngine/Fonts/profont.ttf"

			self.__CurrentLevel = None
			
			## Input handlers
			self.__CurrentHandler = None
			self.__CurrentHandler_js = None
			self.__ScreenSize = (0, 0)
	
		@property
		def CurrentLevel(self):
			return self.__CurrentLevel

		@CurrentLevel.setter
		def CurrentLevel(self, var):
			if isinstance(var, LevelBase):
				self.__CurrentLevel = var
			else:
				raise TypeError("CurrentLevel is an invalid instance!")

		@property
		def ScreenSize(self):
			return self.__ScreenSize

		@ScreenSize.setter
		def ScreenSize(self, var):
			## Return value from pygame.Surface.get_size()
			if len(var) == 4:
				self.__ScreenSize = (var[2], var[3])
			elif len(var) == 2:
				self.ScreenSize = var
			else:
				raise AttributeError("ScreenSize is invalid format. Received: " + str(var))
			#Debug("Set ScreenSize to " + str(var))

		@property
		def CurrentHandler(self):
			return self.__CurrentHandler
		
		@CurrentHandler.setter
		def CurrentHandler(self, handler):
			if isinstance(handle, EventHandler) and not isinstance(handle, JoyHandler):
				#Info("Changing current main handler to " + handler.Name)
				self.__CurrentHandler = handler
			else:
				raise TypeError("CurrentHandler is an invalid type! Found " + str(type(handle)))
				
		@property
		def CurrentHandler_js(self):
			return self.__CurrentHandler_js
			
		@CurrentHandler_js.setter
		def CurrentHandler_js(self, handler):
			if isinstance(handle, JoyHandler):
				#Info("Changing current joy handler to " + handler.Name)
				self.__CurrentHandler_js = handler
			else:
				raise TypeError("CurrentHandler_js is an invalid type! Found " + str(type(handle)))
			
	
	## Singleton stuff below.
	__instance = None
	
	def __init__(self):
		if Vars.__instance == None:
			Vars.__instance = Vars._vars()
		
		self.__dict__['_Singleton_instance'] = Vars.__instance
		
	def __getattr__(self, attr):
		return getattr(self.__instance, attr)
	
	def __setattr__(self, attr, value):
		return setattr(self.__instance, attr, value)
		
#import inspect
#print str(inspect.getframeinfo(inspect.currentframe().f_back))
