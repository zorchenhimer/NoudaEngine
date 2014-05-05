#!/usr/bin/python

import pygame
import random
import Level
import GameObjects
import Projectiles
from Globals import LoadImage, Vars

class Asteroids(Level.LevelBase):
	class BigRock(Projectiles.Projectile):
		def __init__(self):
			imagepathprefix = "png/Meteors/"
			imagelist = [ "meteorBrown_big1.png", "meteorBrown_big2.png", "meteorBrown_big3.png", "meteorBrown_big4.png" ]
			r = random.Random()
			
			vars = Vars()
			startX = r.randint(vars.Bounds.left, vars.Bounds.right)
			startY = r.randint(vars.Bounds.top, vars.Bounds.bottom)
			angle = r.randint(0, 360)
			
			Projectiles.Projectile.__init__(self, startX, startY, angle)
			self.image = LoadImage(imagepathprefix + r.choice(imagelist))
			self.rect = self.image.get_rect()
			
			self.Speed = 0.5
			
	def __init__(self):
		Level.LevelBase.__init__(self, 'Asteroids')
		self.Asteroids = pygame.sprite.Group()
		for i in range(1, 3):
			self.Asteroids.add(Asteroids.BigRock())
	
	def update(self):
		self.Asteroids.update()
	
	def draw(self, screen):
		pass
