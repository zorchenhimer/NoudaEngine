#!/usr/bin/python

## Holds all the vehicle type classes

import math
import pygame
import Globals
import HeadsUpDisplay
from Globals import GTFO, UnitType
from Pathing import MovementPath
from Projectiles import Bullet, BulletBomb
#import random

#RAND = random.Random()

class Vehicle(pygame.sprite.Sprite):
	def __init__(self, Type=UnitType.ENEMY):
		self.vars = Globals.Vars()
		self.type = Type
			
		pygame.sprite.Sprite.__init__(self)
		
		spritePath = ''
		if self.type == UnitType.PLAYER:
			spritePath = 'png/playerShip1_red.png'
		else:
			spritePath = 'png/Enemies/enemyGreen1.png'
		
		self.image = Globals.LoadImage(spritePath)
		self.rect = self.image.get_rect()
		#self.rect.center = self.vars.Bounds.center
		self.vars.gameSprites.add(self)
		self.firing = False
		self.nextFire = 0	# Ticks until next fire
		
		self.movementSpeed = 4
		self.movingLeft = False
		self.movingRight = False
		self.movingUp = False
		self.movingDown = False
		
		self.firstFire = True
		
		self.FireRate = 5
	
	def update(self):
		#if self.type is UnitType.ENEMY and self.path is None:
		#	self.kill() ## lol, is this defined anywhere?

		## Fire a bullet if it's time	
		if self.nextFire > 0:
			self.nextFire -= 1
		
		if self.firing == True:
			if self.nextFire <= 0:
				self.FireBullet()
				self.nextFire = self.FireRate
		
		## Move the vehicle if we haven't gotten the 'stop moving' event yet.
		## This should never trigger for enemy ships.
		if self.movingLeft == True:
			self.rect.centerx -= self.movementSpeed
		if self.movingRight == True:
			self.rect.centerx += self.movementSpeed
			
		if self.movingUp == True:
			self.rect.centery -= self.movementSpeed
		if self.movingDown == True:
			self.rect.centery += self.movementSpeed
		
	def FireBullet(self):
		if self.type == UnitType.ENEMY:
			self.vars.GameProjectiles.add(Bullet(self.type, self.rect.centerx, self.rect.centery, None, 40))
			self.vars.GameProjectiles.add(Bullet(self.type, self.rect.centerx, self.rect.centery, 135, 30))
			self.vars.GameProjectiles.add(Bullet(self.type, self.rect.centerx, self.rect.centery, 225, 30))
		else:
			self.vars.GameProjectiles.add(Bullet(self.type, self.rect.centerx, self.rect.top - 30))
	
	def FireBomb(self):
		self.vars.GameProjectiles.add(BulletBomb(self.type, self.rect.centerx, self.rect.top - 30))
		
	def MoveLeft(self, on=False):
		self.movingLeft = on
	
	def MoveRight(self, on=False):
		self.movingRight = on
	
	def MoveUp(self, on=False):
		self.movingUp = on
	
	def MoveDown(self, on=False):
		self.movingDown = on

	def tostring(self):
		typetext = 'Unknown'
		if self.type == Globals.UnitType.PLAYER:
			typetext = 'player'
		elif self.type == Globals.UnitType.ENEMY:
			typetext = 'enemy'
		return 'Vehicle type: ' + typetext + ' centered at ' + str(self.rect.center)
		
		
class Player(Vehicle):
	def __init__(self):
		Vehicle.__init__(self, UnitType.PLAYER)
		self.rect.centery = self.vars.Bounds.bottom - self.rect.height
		self.rect.centerx = self.vars.Bounds.centerx
		self.firing = False
		self.movementSpeed = 9

	def ToggleFire(self, Firing=False):
		self.firing = Firing
	
	def StopFire(self):
		self.firing = False
		
	def update(self):
		## Keep the vehicle in bounds.
		if self.rect.left < self.vars.Bounds.left:
			self.movingLeft = False
		if self.rect.right > self.vars.Bounds.right:
			self.movingRight = False
			
		if self.rect.top < self.vars.Bounds.top:
			self.movingUp = False
		if self.rect.bottom > self.vars.Bounds.bottom:
			self.movingDown = False
		
		Vehicle.update(self)
	
	## The player's sprite is not in a sprite group, so we have to define this
	## here.
	## FIXME: Put the player in a sprite group, or add draw() to Vehicle()
	def draw(self, screen):
		screen.blit(self.image, self.rect)
	
class Enemy(Vehicle):
	def __init__(self):
		Vehicle.__init__(self)
		self.firing = False
		self.path = None# MovementPath(self)#'enemy-path.dat')
		#self.path.load_basic_path()
		#self.rect.center = self.path.get_position()
	
	def set_path(self, path):
		self.path = path
		self.rect.center = self.path.get_position()
	
	""" AI stuff goes here """
	def update(self):
		self.rect.center = self.path.get_position()
		## Call this explicitly since we override it.
		Vehicle.update(self)
