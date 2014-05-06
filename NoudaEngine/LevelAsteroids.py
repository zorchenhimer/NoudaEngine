#!/usr/bin/python

import pygame
import random
import copy
import math
import Level
import GameObjects
import Projectiles
import HeadsUpDisplay
from Globals import LoadImage, Vars, UnitType, TileImage
from Logger import Debug

class Asteroids(Level.LevelBase):
	class BigRock(Projectiles.Projectile):
		"""
			Biggest Rock.
			TODO: make a base rock class.
		"""
		def __init__(self):
			imagepathprefix = "png/Meteors/"
			imagelist = [ "meteorBrown_big1.png" , "meteorBrown_big2.png", "meteorBrown_big3.png", "meteorBrown_big4.png" ]
			r = random.Random()
			
			vars = Vars()
			startX = r.randint(vars.Bounds.left + 20, vars.Bounds.right - 20)
			startY = r.randint(vars.Bounds.top + 20, vars.Bounds.bottom - 20)
			angle = r.randint(0, 360)
			
			Projectiles.Projectile.__init__(self, angle)
			self.image = LoadImage(imagepathprefix + r.choice(imagelist))
			self.rect = self.image.get_rect()
			self.rect.x = startX
			self.rect.y = startY
			
			self.cx = self.rect.centerx * 1.0
			self.cy = self.rect.centery * 1.0
			
			self.Speed = 1.0
			self.Type = UnitType.ENEMY

			self.Clone = self.rect.copy()
			
			self.calculate_path()

		def update(self):
			vars = Vars()
			self.cx += self.StepX
			self.cy += self.StepY
			
			self.rect.centerx = self.cx
			self.rect.centery = self.cy
			
			if self.cy <= 0:
				self.cy = vars.ScreenSize[1]
			elif self.cy >= vars.ScreenSize[1]:
				self.cy = 1

			if self.cx <= 0:
				self.cx = vars.ScreenSize[0]
			elif self.cx >= vars.ScreenSize[0]:
				self.cx = 1
			
			dist_from_center_x = ((vars.ScreenSize[0] / 2) - self.cx) * -1
			dist_from_center_y = ((vars.ScreenSize[1] / 2) - self.cy) * -1

			dist_from_top = self.cy
			dist_from_left = self.cx
			dist_from_bottom = vars.ScreenSize[1] - self.cy
			dist_from_right = vars.ScreenSize[0] - self.cx

			if dist_from_top < dist_from_left and dist_from_top < dist_from_right and dist_from_top < dist_from_bottom:
				# Closest to top
				self.Clone.centerx = self.cx
				self.Clone.centery = self.cy + vars.ScreenSize[1]
			elif dist_from_bottom < dist_from_left and dist_from_bottom < dist_from_right:
				# Closest to bottom
				self.Clone.centerx = self.cx
				self.Clone.centery = self.cy - vars.ScreenSize[1]
			elif dist_from_left < dist_from_right:
				# Closest to left
				self.Clone.centerx = self.cx + vars.ScreenSize[0]
				self.Clone.centery = self.cy
			else:
				# Closest to right
				self.Clone.centerx = self.cx - vars.ScreenSize[0]
				self.Clone.centery = self.cy

		def draw(self, screen):
			screen.blit(self.image, self.rect)
			screen.blit(self.image, self.Clone)

		def check_bounds(self):
			return False
			
	def __init__(self):
		Level.LevelBase.__init__(self, 'Asteroids')
		self.Asteroids = pygame.sprite.Group()
		self.Started = False

		self.Background = TileImage('png/Backgrounds/black.png')
	
	def reset(self):
		self.Asteroids.empty()
		self.Started = False
	
	def start_level(self):
		self.Started = True
		for i in range(0, 4):
			self.Asteroids.add(Asteroids.BigRock())
	
	def update(self):
		if self.Started is False:
			self.start_level()
		self.Asteroids.update()
	
	def draw(self, screen):
		screen.blit(self.Background, (0,0))
		for a in self.Asteroids:
			a.draw(screen)
	
	def init_controls(self):
		pass
