#!/usr/bin/python

import pygame
import random
import copy
import Level
import GameObjects
import Projectiles
import HeadsUpDisplay
from Globals import LoadImage, Vars, UnitType, TileImage
from Logger import Debug


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
			
			Projectiles.Projectile.__init__(self, angle)
			self.image = LoadImage(imagepathprefix + r.choice(imagelist))
			self.rect = self.image.get_rect()
			self.rect.x = startX
			self.rect.y = startY
			
			self.Speed = 1.0
			self.Type = UnitType.ENEMY

			self.Clone = None
			self.IsClone = False

			self.calculate_path()
			Debug("Spawning asteroid at " + str((startX, startY)))
			Debug("Vector: " + str((self.StepX, self.StepY)) + "(" + str(angle) + ") Speed: " + str(self.Speed))

		def update(self):
			#Projectiles.Projectile.update(self, True)
			self.rect.centerx += self.StepX
			self.rect.centery += self.StepY
			
			hud = HeadsUpDisplay.HUD()
			hud.set_text(HeadsUpDisplay.Locations.TOPLEFT, str(self.rect.center))
			
			vars = Vars()
			if self.IsClone is False:
				if self.rect.centery <= 0:
					self.rect.centery = vars.ScreenSize[1]
					Debug("BigRock hit top of screen; moving to bottom. (" + str(self.rect.center) + ")")
				elif self.rect.centery >= vars.ScreenSize[1]:
					self.rect.centery = 1
					Debug("BigRock hit bottom of screen; moving to top. (" + str(self.rect.center) + ")")

				if self.rect.centerx <= 0:
					self.rect.centerx = vars.ScreenSize[0]
					Debug("BigRock hit left of screen; moving to right. (" + str(self.rect.center) + ")")
				elif self.rect.centerx >= vars.ScreenSize[0]:
					self.rect = 1
					Debug("BigRock hit right of screen; moving to left. (" + str(self.rect.center) + ")")
				
				if self.Clone is None:
					if self.rect.left <= 0:
						self.Clone = self.clone(self.rect.x + vars.ScreenSize[0], self.rect.y)
						#self.Clone.rect.centerx = self.rect.centerx + vars.ScreenSize[0]
					elif self.rect.right >= vars.ScreenSize[0]:
						self.Clone = self.clone(self.rect.x * -1, self.rect.y)
						#self.Clone.rect.centerX = self.rect.centerx * -1

					if self.rect.top <= 0:
						self.Clone = self.clone(self.rect.x, self.rect.y + vars.ScreenSize[1])
						#self.Clone.rect.centery = self.rect.centery + vars.ScreenSize[1]
					elif self.rect.bottom >= vars.ScreenSize[1]:
						self.Clone = self.clone(self.rect.x, self.rect.y + -1)
						#self.Clone.rect.centery = self.rect.centery * -1
				else:
					self.Clone.update()
			
			#FIXME: Move the clone to its own class.  Currently borked.
			elif self.IsClone is True:
				if (self.rect.left > 0 and self.rect.right < vars.ScreenSize[0]) and (self.rect.top > 0 and self.rect.bottom < vars.ScreenSize[1]):
					#Debug("Clone destroyed.")
					self.kill()
					#Debug("Attempted to kill. " + str(self.rect))
			
		def draw(self, screen):
			if self.IsClone is True:
				#if (self.rect.right > 0 and self.rect.left < vars.ScreenSize[0]) or (self.rect.top > 0 and self.rect.bottom < vars.ScreenSize[1]):
				screen.blit(self.image, self.rect)
				self.Clone.draw(screen)
			else:
				screen.blit(self.image, self.rect)


		def clone(self, x, y):
			Debug("Attempting to create clone at " + str((x, y)))
			c = copy.deepcopy(self)
			c.IsClone = True
			c.rect.x = x
			c.rect.y = y
			Debug("self location: " + str(self.rect))
			return c

		def check_bounds(self):
			return False
			
	def __init__(self):
		Level.LevelBase.__init__(self, 'Asteroids')
		self.Asteroids = pygame.sprite.Group()
		for i in range(0, 1):
			self.Asteroids.add(Asteroids.BigRock())

		self.Background = TileImage('png/Backgrounds/black.png')
	
	def update(self):
		self.Asteroids.update()
	
	def draw(self, screen):
		screen.blit(self.Background, (0,0))
		self.Asteroids.draw(screen)
	
	def init_controls(self):
		pass
