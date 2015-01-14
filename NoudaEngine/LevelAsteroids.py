#!/usr/bin/python

import pygame
import random
import copy
import math
import Level
import GameObjects
import Projectiles
import HeadsUpDisplay
from Globals import LoadImage, Vars, UnitType, TileImage, DebugPause
from Logger import Debug

def get_linear(tuple):
	return math.sqrt(tuple[0]**2 + tuple[1]**2)

class Asteroids(Level.LevelBase):
	class RockSizes():
		BIG = 3
		MED = 2
		SMALL = 1
		TINY = 0
	
	class WrappingObject():
		def __init__(self):
			pass
		
		def update(self):
			pass
		
	class Rock(Projectiles.Projectile):
		def __init__(self, stX=None, stY=None, sAngle=None, rocksize=3):
			Projectiles.Projectile.__init__(self, sAngle)
			imagepathprefix = "png/Meteors/"
			r = random.Random()
			
			self.Children = pygame.sprite.Group()
			self.RockSize = rocksize
			self.Exploded = False
			self.Collided = False
			
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
				startX = r.randint(pygame.display.get_surface().get_rect().left + 20, pygame.display.get_surface().get_rect().right - 20)
			else:
				startX = stX
			
			if stY is None:
				startY = r.randint(pygame.display.get_surface().get_rect().top + 20, pygame.display.get_surface().get_rect().bottom - 20)
			else:
				startY = stY
			
			if sAngle is None:
				self.Degrees = r.randint(0, 360)
			
			self.image = LoadImage(str(imagepathprefix) + str(r.choice(imglist)))
			self.rect = self.image.get_rect()
			self.mask = pygame.mask.from_surface(self.image)
			self.rect.centerx = startX
			self.rect.centery = startY
			
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
		
		## FIXME: do an angular change instead of just inverting the speed.  It looks
		##        really weird just reversing  when rocks graze eachother.
		def do_collide(self):
			if self.Collided is False:
				self.Speed *= -1
				self.calculate_path()
				self.Collided = True
				Debug("Collided with something!")

		def update(self):
			if self.Collided is True:
				self.Collided = False
			if self.Exploded is True:
				self.Children.update()
				return
				
			vars = Vars()
			self.cx += self.StepX
			self.cy += self.StepY
			
			
			if self.cy < 0:
				self.cy = pygame.display.get_surface().get_size()[1]
			elif self.cy > pygame.display.get_surface().get_size()[1]:
				self.cy = 0

			if self.cx < 0:
				self.cx = pygame.display.get_surface().get_size()[0]
			elif self.cx > pygame.display.get_surface().get_size()[0]:
				self.cx = 0
				
			self.rect.centerx = self.cx
			self.rect.centery = self.cy

			## Draw the rock on the oposite edge of the screen
			dist_from_top = self.cy
			dist_from_left = self.cx
			dist_from_bottom = pygame.display.get_surface().get_size()[1] - self.cy
			dist_from_right = pygame.display.get_surface().get_size()[0] - self.cx

			if dist_from_top < dist_from_left and dist_from_top < dist_from_right and dist_from_top < dist_from_bottom:
				# Closest to top
				self.Clone.centerx = self.cx
				self.Clone.centery = self.cy + pygame.display.get_surface().get_size()[1]
			elif dist_from_bottom < dist_from_left and dist_from_bottom < dist_from_right:
				# Closest to bottom
				self.Clone.centerx = self.cx
				self.Clone.centery = self.cy - pygame.display.get_surface().get_size()[1]
			elif dist_from_left < dist_from_right:
				# Closest to left
				self.Clone.centerx = self.cx + pygame.display.get_surface().get_size()[0]
				self.Clone.centery = self.cy
			else:
				# Closest to right
				self.Clone.centerx = self.cx - pygame.display.get_surface().get_size()[0]
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
				self.rect.centery = pygame.display.get_surface().get_size()[1]
			elif self.rect.centery > pygame.display.get_surface().get_size()[1]:
				self.rect.centery = 0

			if self.rect.centerx < 0:
				self.rect.centerx = pygame.display.get_surface().get_size()[0]
			elif self.rect.centerx > pygame.display.get_surface().get_size()[0]:
				self.rect.centerx = 0

			## Draw the bullet on the oposite edge
			dist_from_top = self.rect.centery
			dist_from_left = self.rect.centerx
			dist_from_bottom = pygame.display.get_surface().get_size()[1] - self.rect.centery
			dist_from_right = pygame.display.get_surface().get_size()[0] - self.rect.centerx

			if dist_from_top < dist_from_left and dist_from_top < dist_from_right and dist_from_top < dist_from_bottom:
				# Closest to top
				self.Clone.centerx = self.rect.centerx
				self.Clone.centery = self.rect.centery + pygame.display.get_surface().get_size()[1]
			elif dist_from_bottom < dist_from_left and dist_from_bottom < dist_from_right:
				# Closest to bottom
				self.Clone.centerx = self.rect.centerx
				self.Clone.centery = self.rect.centery - pygame.display.get_surface().get_size()[1]
			elif dist_from_left < dist_from_right:
				# Closest to left
				self.Clone.centerx = self.rect.centerx + pygame.display.get_surface().get_size()[0]
				self.Clone.centery = self.rect.centery
			else:
				# Closest to right
				self.Clone.centerx = self.rect.centerx - pygame.display.get_surface().get_size()[0]
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
			
			self.TurnSpeed = 3
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
				self.cy = pygame.display.get_surface().get_size()[1]
			elif self.cy > pygame.display.get_surface().get_size()[1]:
				self.cy = 0

			if self.cx < 0:
				self.cx = pygame.display.get_surface().get_size()[0]
			elif self.cx > pygame.display.get_surface().get_size()[0]:
				self.cx = 0

			## Draw a cloned ship on the oposite edge of the screen
			dist_from_top = self.cy
			dist_from_left = self.cx
			dist_from_bottom = pygame.display.get_surface().get_size()[1] - self.cy
			dist_from_right = pygame.display.get_surface().get_size()[0] - self.cx

			if dist_from_top < dist_from_left and dist_from_top < dist_from_right and dist_from_top < dist_from_bottom:
				# Closest to top
				self.Clone.centerx = self.cx
				self.Clone.centery = self.cy + pygame.display.get_surface().get_size()[1]
			elif dist_from_bottom < dist_from_left and dist_from_bottom < dist_from_right:
				# Closest to bottom
				self.Clone.centerx = self.cx
				self.Clone.centery = self.cy - pygame.display.get_surface().get_size()[1]
			elif dist_from_left < dist_from_right:
				# Closest to left
				self.Clone.centerx = self.cx + pygame.display.get_surface().get_size()[0]
				self.Clone.centery = self.cy
			else:
				# Closest to right
				self.Clone.centerx = self.cx - pygame.display.get_surface().get_size()[0]
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
		#self.Asteroids.add(Asteroids.Rock(300, 300, 90))
		#self.Asteroids.add(Asteroids.Rock(600, 250, 270))
	
	def update(self):
		if self.Started is False:
			self.start_level()
		self.Asteroids.update()
		self.Player.update()
		
		allrocks = pygame.sprite.Group()
		for r in self.Asteroids:
			allrocks.add(r.get_sprites())
		
		bullet_collisions = pygame.sprite.groupcollide(allrocks, self.Player.Projectiles, False, True)
		for c in bullet_collisions:
			c.explode()

		"""for rock in allrocks:
			crocks = pygame.sprite.spritecollide(rock, allrocks, False)
			for cr in crocks:
				if cr != rock:
					cr.do_collide()
			if len(crocks) == 1:
				rock.Collided = False"""

		## FIXME: This doesn't work at all.  Keeps inverting the vectors after the first collision.  Calculated vectors are probably wrong too...
		for rock in allrocks:
			for other_rock in allrocks:
				if rock != other_rock and pygame.sprite.collide_mask(rock, other_rock) is not None:
					Debug('== Collision ==')
					if rock.Collided is False:
						rock.Collided = True
						other_rock.Collided = True
						
						## Find the triangle.
						Ax = rock.cx
						Ay = rock.cy
						Bx = other_rock.cx
						By = other_rock.cy
						Cx = Ax
						Cy = By
						
						## Get the Angles of said triangle.
						B_deg = abs(math.degrees(math.atan((Ay - By)/(Ax - Bx))))
						A_deg = 90 - B_deg
						
						## Add the angles to the oposite rock.
						rock.Degrees += B_deg
						other_rock.Degrees += A_deg
						
						## Re-calculate rock vectors.
						rock.Offset = 5
						other_rock.Offset = 5
						rock.calculate_path()
						other_rock.calculate_path()
						
						Debug(".rock ({ax}, {ay})".format(ax=Ax, ay=Ay))
						Debug(".other_rock ({bx}, {by})".format(bx=Bx, by=By))
						Debug("..Point C ({cx}, {cy})".format(cy=Cy, cx=Cx))
						Debug("..A_deg: {deg}".format(deg=A_deg))
						Debug("..B_deg: {deg}".format(deg=B_deg))
					else:
						Debug('~~ Resetting collison bool ~~')
						rock.Collided = False
						other_rock.Collided = False
	
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

		self.JoyHandle.add_joyhold_handle('a1neg', self.Player.MoveForward)
		self.JoyHandle.add_joyhold_handle('a0pos', self.Player.TurnRight)
		self.JoyHandle.add_joyhold_handle('a0neg', self.Player.TurnLeft)
		self.JoyHandle.add_joyhold_handle(1, self.Player.Fire)

