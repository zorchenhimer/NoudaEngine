#!/usr/bin/python

import math
import pygame
import Globals
from Globals import UnitType
import Effects

## TODO: add custom paths option
class Bullet(pygame.sprite.Sprite):
	""" All projectiles will inherit this class for a basic projectile. """		
	def __init__(self, t, x, y, d=None, l=-1):
		pygame.sprite.Sprite.__init__(self)
		
		self.Type = t
		self.Speed = 6		# Movementper tick
		self.Degrees = d
		self.Life = l		## Anything higher than -1 will determine how many 
							## ticks the projectile is alive.
		
		## Defaults given the unit type that fired the projectile.
		if self.Degrees == None:
			if self.Type == UnitType.PLAYER:
				self.Degrees = 0
			elif self.Type == UnitType.ENEMY:
				self.Degrees = 180
			else:
				self.Degrees = 90
		
		self.Radian = (self.Degrees - 90) * (math.pi / 180)
		
		## Load the correct image.
		self.image = None
		if self.Type == UnitType.PLAYER:
			self.image = pygame.transform.rotate(Globals.LoadImage('png/Lasers/laserGreen02.png'), (self.Degrees * -1))
			self.Speed = 15
		else:
			self.image = pygame.transform.rotate(Globals.LoadImage('png/Lasers/laserRed02.png'), (self.Degrees * -1))
		
		self.image
		
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		
		## Distance the projectile travels per tick, given the angle above.
		self.StepX = self.Speed * math.cos(self.Radian)
		self.StepY = self.Speed * math.sin(self.Radian)
	
	def check_bounds(self):
		vars = Globals.Vars()
		bounds = vars.Bounds
		if self.Type == UnitType.ENEMY:
			bounds = vars.ScreenSize
		
		if self.Life > -1:
			if self.Life == 0:
				return False
			else:
				self.Life -= 1
		
		if bounds.contains(self.rect):
			return True
		return False
	
	def update(self):
		## This will despawn the projectile once it leaves play.
		if not self.check_bounds():
			self.kill()
		
		## Move the projectile keeping in mind the direction.
		self.rect.x += self.StepX
		self.rect.y += self.StepY
		
		vars = Globals.Vars()
		
		collisions = pygame.sprite.groupcollide(vars.GameEnemies, vars.GameProjectiles, True, False)
		for sp in collisions:
			vars.GameProjectiles.add(Effects.Explosion(self.Type, self.rect.center))
			self.kill()

class BulletBomb(Bullet):
	def __init__(self, t, x, y, d=0, l=90):
		Bullet.__init__(self, t, x, y, d, l)
		self.Fuse = 20
		self.Speed = 1
	
	def detonate(self):
		vars = Globals.Vars()
		for n in range(10):
			vars.GameProjectiles.add(BulletBomb(self.Type, self.rect.centerx, self.rect.centery, (n * 36), self.Life - 20))
		vars.GameProjectiles.add(Effects.Explosion(self.Type, self.rect.center))
		self.kill()
	
	def update(self):
		if self.Fuse > 0:
			self.Fuse -= 1
			Bullet.update(self)
		else:
			self.detonate()
