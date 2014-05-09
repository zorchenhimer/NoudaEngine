#!/usr/bin/python

## Holds variables and objects that are needed by a bunch of different classes

import pygame
import platform
import os.path as path
import math
from Logger import Debug, Warn, Info

## This needs to move to GameObjects
class UnitType():
	PLAYER = 1
	ENEMY = 2

## This might be better in GameEngine().
class GameState():
	""" Top level game states. """
	MENU = 1
	GAME = 2
	GAMEOVER = 3

def LoadImage(path):
	""" Return a surface containing the image at the given path. """
	surf = None
	path = FixPath(path)
	try:
		surf = pygame.Surface.convert_alpha(pygame.image.load(path))
	except Exception as exc:
		print("Unable to load image at path '" + path + "': " + str(exc))
	return surf

def FixPath(p):
	""" Return the correct path format depending on the current system. """
	if platform.system().lower() == 'windows':
		return path.abspath(p.replace('/', '\\'))
	else:
		return path.abspath(p.replace('\\', '/'))

def TileImage(surf):
	"""
		Return a new surface the size of the screen with the given
		surface tiled in both directions.
	"""

	vars = Vars()
	if isinstance(surf, pygame.Surface):
		newsurf = pygame.Surface(vars.ScreenSize)
		widthRepeat = int(math.ceil(newsurf.get_width() / surf.get_width()))
		heightRepeat = int(math.ceil(newsurf.get_height() / surf.get_height()))
		
		(surfW, surfH) = surf.get_size()
		for h in range(0, heightRepeat + 1):
			for w in range(0, widthRepeat + 1):
				newsurf.blit(surf, (w * surfW, h * surfH))
	else:
		return TileImage(LoadImage(surf))
	return newsurf

class Vars():
	## Actual class here.
	class _vars:
		def __init__(self):
			self.Running = True
			self.DefaultFontPath = "NoudaEngine/Fonts/profont.ttf"
			
			## Input handlers
			self.__CurrentHandler = None
			self.__CurrentHandler_js = None
			self.__ScreenSize = (0, 0)
			
			Info("Global.Vars() has been initialized.")
		
		## TODO: Make everything that calls this use pygame.display.get_surface() instead
		@property
		def ScreenSize(self):
			return self.__ScreenSize

		@ScreenSize.setter
		def ScreenSize(self, var):
			## Return value from pygame.Surface.get_size()
#			if len(var) == 4:
				self.__ScreenSize = var
#			elif len(var) == 2:
#				self.__ScreenSize = var
#			else:
#				raise AttributeError("ScreenSize is invalid format. Received: " + str(var))

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
