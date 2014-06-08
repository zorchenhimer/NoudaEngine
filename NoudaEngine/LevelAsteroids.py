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

def get_linear(tuple):
	return math.sqrt(tuple[0]**2 + tuple[1]**2)

class Asteroids(Level.LevelBase):
	class RockSizes():
		BIG = 3
		MED = 2
		SMALL = 1
		TINY = 0
		
	class Rock(Projectiles.Projectile):
		"""
			Rock.
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
		
		def get_sprites(self):
			if self.Exploded == False:
				return self
			else:
				ret = []
				for c in self.Children:
					ret.append(c.get_sprites())
				return ret
		
		def explode(self):
			rand = random.Random()
			if self.RockSize > Asteroids.RockSizes.TINY:
				if self.Exploded is False:
					for i in range(0, 2):
						srock = Asteroids.Rock(self.cx, self.cy, self.Degrees + (i * 180) + rand.randint(-90, 90), self.RockSize - 1)
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
	
	class WrappingBullet(Projectiles.Bullet):
		def __init__(self, t, x, y, d=None, l=-1):
			Projectiles.Bullet.__init__(self, t, x, y, d, l, 3)
			self.Clone = self.rect.copy()
			
		def check_bounds(self):
			return True
		
		def update(self):
			Projectiles.Bullet.update(self)
			vars = Vars()
			if self.rect.centery < 0:
				self.rect.centery = vars.ScreenSize[1]
			elif self.rect.centery > vars.ScreenSize[1]:
				self.rect.centery = 0

			if self.rect.centerx < 0:
				self.rect.centerx = vars.ScreenSize[0]
			elif self.rect.centerx > vars.ScreenSize[0]:
				self.rect.centerx = 0

			dist_from_top = self.rect.centery
			dist_from_left = self.rect.centerx
			dist_from_bottom = vars.ScreenSize[1] - self.rect.centery
			dist_from_right = vars.ScreenSize[0] - self.rect.centerx

			if dist_from_top < dist_from_left and dist_from_top < dist_from_right and dist_from_top < dist_from_bottom:
				# Closest to top
				self.Clone.centerx = self.rect.centerx
				self.Clone.centery = self.rect.centery + vars.ScreenSize[1]
			elif dist_from_bottom < dist_from_left and dist_from_bottom < dist_from_right:
				# Closest to bottom
				self.Clone.centerx = self.rect.centerx
				self.Clone.centery = self.rect.centery - vars.ScreenSize[1]
			elif dist_from_left < dist_from_right:
				# Closest to left
				self.Clone.centerx = self.rect.centerx + vars.ScreenSize[0]
				self.Clone.centery = self.rect.centery
			else:
				# Closest to right
				self.Clone.centerx = self.rect.centerx - vars.ScreenSize[0]
				self.Clone.centery = self.rect.centery
				
		
		def draw(self, screen):
			screen.blit(self.image, self.rect)
			screen.blit(self.image, self.Clone)
	
	class Player(pygame.sprite.Sprite):
		def __init__(self):
			pygame.sprite.Sprite.__init__(self)
			vars = Vars()
			
			self.Projectiles = pygame.sprite.Group()
			self.image = LoadImage('png/playerShip1_green.png')
			disprect = pygame.display.get_surface().get_rect()
			
			self.TurnSpeed = 2
			self.Rotation = 0
			self.Thrust = 0.02		# pixels per tick per tick
			self.Speed = 0.0
			self.Velocity = [0, 0]
			self.NextFire = 0
			self.FireRate = 10
			self.Firing = False
			
			## 0 is 'false', +/-# is 'true'
			self.Rotating = 0
			self.Thrusting = 0
			
			self.imagerot = pygame.transform.rotate(self.image, self.Rotation)
			self.rect = self.imagerot.get_rect()
			self.cx = disprect.centerx
			self.cy = disprect.bottom - 150
			
			self.Clone = self.rect.copy()
		
		def update(self):
			#hud = HeadsUpDisplay.HUD()
			if self.Thrusting > 0 and self.Speed < 0.05:
				self.Speed += self.Thrust
			elif self.Thrusting < 0:
				self.Speed -= self.Thrust
			
			if self.Rotating > 0:
				self.Rotation += self.TurnSpeed
				if self.Rotation > 360:
					self.Rotation -= 360
			elif self.Rotating < 0:
				self.Rotation -= self.TurnSpeed
				if self.Rotation < 0:
					self.Rotation += 360
			
			
			radian = (self.Rotation - 90) * (math.pi / 180)
			
			if self.Rotating != 0:
				self.imagerot = pygame.transform.rotozoom(self.image, self.Rotation * -1, 1)
				self.rotrect = self.imagerot.get_rect()
				self.rotrect.center = self.rect.center
				self.rect = self.rotrect
				self.Clone = self.rect.copy()
			
			if self.Thrusting != 0:
				self.Velocity = (self.Velocity[0] + self.Speed * math.cos(radian), self.Velocity[1] + self.Speed * math.sin(radian))
			
			self.cx += self.Velocity[0]
			self.cy += self.Velocity[1]
			
			vars = Vars()
			if self.cy < 0:
				self.cy = vars.ScreenSize[1]
			elif self.cy > vars.ScreenSize[1]:
				self.cy = 0

			if self.cx < 0:
				self.cx = vars.ScreenSize[0]
			elif self.cx > vars.ScreenSize[0]:
				self.cx = 0
			
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
			
			self.rect.center = (self.cx, self.cy)

			if self.NextFire > 0:
				self.NextFire -= 1
			
			if self.Firing:
				if self.NextFire <= 0:
					self.Projectiles.add(Asteroids.WrappingBullet(UnitType.PLAYER, self.cx, self.cy, self.Rotation, 50))
					self.NextFire = self.FireRate
			
			self.Projectiles.update()
			
		def draw(self, screen):
			screen.blit(self.imagerot, self.rect)
			screen.blit(self.imagerot, self.Clone)
			for p in self.Projectiles:
				p.draw(screen)
		
		def MoveForward(self, on=False):
			if on:
				Debug("Moving Forward")
				self.Thrusting += 1
			else:
				self.Thrusting -= 1
		
		def MoveBackward(self, on=False):
			pass
		
		def TurnLeft(self, on=False):
			if on:
				self.Rotating -= 1
			else:
				self.Rotating += 1
		
		def TurnRight(self, on=False):
			if on:
				self.Rotating += 1
			else:
				self.Rotating -= 1
		
		def Fire(self, on=False):
			self.Firing = on
	
	def __init__(self):
		Level.LevelBase.__init__(self, 'Asteroids')
		self.Asteroids = pygame.sprite.Group()
		self.Started = False

		self.Background = TileImage('png/Backgrounds/black.png')
		self.Player = Asteroids.Player()
	
	def reset(self):
		self.Asteroids.empty()
		self.Started = False
		self.Player = Asteroids.Player()
	
	def start_level(self):
		self.Started = True
		for i in range(0, 5):
			self.Asteroids.add(Asteroids.Rock())
	
	def update(self):
		if self.Started is False:
			self.start_level()
		self.Asteroids.update()
		self.Player.update()
		
		allrocks = pygame.sprite.Group()
		for r in self.Asteroids:
			allrocks.add(r.get_sprites())
		
		collisions = pygame.sprite.groupcollide(allrocks, self.Player.Projectiles, False, True)
		for c in collisions:
			c.explode()
	
	def draw(self, screen):
		screen.blit(self.Background, (0,0))
		for a in self.Asteroids:
			a.draw(screen)
		self.Player.draw(screen)
	
	def explode_all_the_things(self):
		for a in self.Asteroids:
			a.explode()
	
	def init_controls(self):
		self.KeyHandle.add_keyhold_handle(pygame.K_SPACE, self.Player.Fire)
		self.KeyHandle.add_keyhold_handle(pygame.K_UP, self.Player.MoveForward)
		self.KeyHandle.add_keyhold_handle(pygame.K_LEFT, self.Player.TurnLeft)
		self.KeyHandle.add_keyhold_handle(pygame.K_RIGHT, self.Player.TurnRight)
