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
	class RockSizes():
		BIG = 3
		MED = 2
		SMALL = 1
		TINY = 0
		
	class Rock(Projectiles.Projectile):
		"""
			Biggest Rock.
			TODO: make a base rock class.
		"""
		def __init__(self, stX=None, stY=None, sAngle=None, rocksize=None):
			Projectiles.Projectile.__init__(self, sAngle)
			imagepathprefix = "png/Meteors/"
			r = random.Random()
			
			self.Children = pygame.sprite.Group()
			self.RockSize = rocksize
			self.Exploded = False
			
			if self.RockSize is None:
				self.RockSize = Asteroids.RockSizes.BIG
			
			imglist = None
			if self.RockSize is Asteroids.RockSizes.BIG:
				imglist = [ "meteorBrown_big1.png", "meteorBrown_big2.png", "meteorBrown_big3.png", "meteorBrown_big4.png" ]
			elif self.RockSize is Asteroids.RockSizes.MED:
				imglist = [ "meteorBrown_med1.png", "meteorBrown_med3.png" ]
			elif self.RockSize is Asteroids.RockSizes.SMALL:
				imglist = [ "meteorBrown_small1.png", "meteorBrown_small2.png" ]
			elif self.RockSize is Asteroids.RockSizes.TINY:
				imglist = [ "meteorBrown_tiny1.png", "meteorBrown_tiny2.png" ]
			else:
				imglist = [ "meteorGrey_tiny1.png", "meteorGrey_tiny2.png" ]
			
			vars = Vars()
			if stX is None:
				startX = r.randint(vars.Bounds.left + 20, vars.Bounds.right - 20)
			else:
				startX = stX
			
			if stY is None:
				startY = r.randint(vars.Bounds.top + 20, vars.Bounds.bottom - 20)
			else:
				startY = stY
			
			if sAngle is None:
				self.Degrees = r.randint(0, 360)
			
			self.image = LoadImage(str(imagepathprefix) + str(r.choice(imglist)))
			self.rect = self.image.get_rect()
			self.rect.x = startX
			self.rect.y = startY
			
			self.cx = self.rect.centerx * 1.0
			self.cy = self.rect.centery * 1.0
			
			self.Speed = 1.0
			self.Type = UnitType.ENEMY

			self.Clone = self.rect.copy()
			
			self.calculate_path()
		
		def explode(self):
			if self.RockSize > Asteroids.RockSizes.TINY:
				if self.Exploded is False:
					for i in range(0, 4):
						srock = Asteroids.Rock(self.cx, self.cy, self.Degrees + (i * 90), self.RockSize - 1)
						srock.Speed += 1.0
						srock.calculate_path()
						self.Children.add(srock)
					self.Exploded = True
				else:
					for a in self.Children:
						a.explode()
			else:
				self.kill()
		
		def update(self):
			if self.Exploded is True:
				self.Children.update()
				return
				
			vars = Vars()
			self.cx += self.StepX
			self.cy += self.StepY
			
			
			if self.cy < 0:
				self.cy = vars.ScreenSize[1]
			elif self.cy > vars.ScreenSize[1]:
				self.cy = 0

			if self.cx < 0:
				self.cx = vars.ScreenSize[0]
			elif self.cx > vars.ScreenSize[0]:
				self.cx = 0
				
			self.rect.centerx = self.cx
			self.rect.centery = self.cy

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
			if self.Exploded is True:
				for a in self.Children:
					a.draw(screen)
			else:
				screen.blit(self.image, self.Clone)
				screen.blit(self.image, self.rect)

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
		for i in range(0, 5):
			self.Asteroids.add(Asteroids.Rock())
	
	def update(self):
		if self.Started is False:
			self.start_level()
		self.Asteroids.update()
	
	def draw(self, screen):
		screen.blit(self.Background, (0,0))
		for a in self.Asteroids:
			a.draw(screen)
	
	def explode_all_the_things(self):
		for a in self.Asteroids:
			a.explode()
	
	def init_controls(self):
		self.KeyHandle.add_keydown_handle(pygame.K_SPACE, self.explode_all_the_things)
