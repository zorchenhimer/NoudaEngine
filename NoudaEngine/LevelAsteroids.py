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
	class RockClone():
		def __init__(self):
			self.image = LoadImage('png/Meteors/meteorGrey_big1.png')
			self.rect = self.image.get_rect()
			vars = Vars()
			
			self.TopRect = pygame.Rect(0,0, vars.ScreenSize[0], vars.ScreenSize[1] / 2)
			self.LeftRect = pygame.Rect(0,0, vars.ScreenSize[0] / 2, vars.ScreenSize[1])
			
			self.TRColor = pygame.Color('darkred')
			self.LRColor = pygame.Color('darkblue')
			self.linecolor = pygame.Color('black')
			
			self.TRColor.a = 127
			self.LRColor.a = 127
		
		def draw(self, screen):
			vars = Vars()
			screen.blit(self.image, self.rect)
			pygame.draw.line(screen, self.linecolor, (self.rect.centerx, self.rect.centery), (vars.ScreenSize[0] / 2, vars.ScreenSize[1] / 2))
		
		def draw_rect(self, screen):
			vars = Vars()
			tmpscr = pygame.Surface(vars.ScreenSize, flags=pygame.SRCALPHA)
			pygame.draw.rect(tmpscr, self.TRColor, self.TopRect)
			pygame.draw.rect(tmpscr, self.LRColor, self.LeftRect)
			screen.blit(tmpscr, (0,0))
			
	class BigRock(Projectiles.Projectile):
		def __init__(self):
			imagepathprefix = "png/Meteors/"
			imagelist = [ "meteorBrown_big1.png" ]#, "meteorBrown_big2.png", "meteorBrown_big3.png", "meteorBrown_big4.png" ]
			r = random.Random()
			
			vars = Vars()
			startX = vars.ScreenSize[0] / 2#r.randint(vars.Bounds.left + 20, vars.Bounds.right - 20)
			startY = vars.ScreenSize[1] / 2#r.randint(vars.Bounds.top + 20, vars.Bounds.bottom - 20)
			angle = 22.5#r.randint(0, 360)
			self.linecolor = pygame.Color('black')
			
			Projectiles.Projectile.__init__(self, angle)
			self.image = LoadImage(imagepathprefix + r.choice(imagelist))
			self.rect = self.image.get_rect()
			self.rect.x = startX
			self.rect.y = startY
			
			self.cx = self.rect.centerx * 1.0
			self.cy = self.rect.centery * 1.0
			
			self.Speed = 1.0
			self.Type = UnitType.ENEMY

			#self.Clone = Asteroids.RockClone(self)
			self.Clones = []
			
			cpy = self.rect.copy()
			cpy.centerx -= vars.ScreenSize[0]
			cpy.centery -= vars.ScreenSize[1]
			self.Clones.append(cpy)
			
			cpy = self.rect.copy()
			cpy.centerx -= vars.ScreenSize[0]
			cpy.centery += vars.ScreenSize[1]
			self.Clones.append(cpy)
			
			cpy = self.rect.copy()
			cpy.centerx += vars.ScreenSize[0]
			cpy.centery -= vars.ScreenSize[1]
			self.Clones.append(cpy)
			
			cpy = self.rect.copy()
			cpy.centerx += vars.ScreenSize[0]
			cpy.centery += vars.ScreenSize[1]
			self.Clones.append(cpy)
			
			self.horizontal = vars.ScreenSize[0] / 2
			self.vertical = vars.ScreenSize[1] / 2
			
			self.calculate_path()
			Debug("Spawning asteroid at " + str((startX, startY)))
			Debug("Vector: " + str((self.StepX, self.StepY)) + "(" + str(angle) + ") Speed: " + str(self.Speed) + " Step: " + str((self.StepX, self.StepY)))

		def update(self):
			vars = Vars()
			#Projectiles.Projectile.update(self, True)
			self.cx += self.StepX
			self.cy += self.StepY
			
			self.rect.centerx = self.cx
			self.rect.centery = self.cy
			
			self.Clones[0].centerx = self.cx - vars.ScreenSize[0]
			self.Clones[0].centery = self.cy - vars.ScreenSize[1]
			
			self.Clones[1].centerx = self.cx - vars.ScreenSize[0]
			self.Clones[1].centery = self.cy + vars.ScreenSize[1]
			
			self.Clones[2].centerx = self.cx + vars.ScreenSize[0]
			self.Clones[2].centery = self.cy - vars.ScreenSize[1]
			
			self.Clones[3].centerx = self.cx + vars.ScreenSize[0]
			self.Clones[3].centery = self.cy + vars.ScreenSize[1]
			
			hud = HeadsUpDisplay.HUD()
			hud.set_text(HeadsUpDisplay.Locations.TOPLEFT, str((self.cx, self.cy)))
			
			if self.cy <= 0:
				self.cy = vars.ScreenSize[1]
			elif self.cy >= vars.ScreenSize[1]:
				self.cy = 1

			if self.cx <= 0:
				self.cx = vars.ScreenSize[0]
			elif self.cx >= vars.ScreenSize[0]:
				self.cx = 1
			
			#self.Clone.update()
			
			dist_from_center_x = ((vars.ScreenSize[0] / 2) - self.cx) * -1
			dist_from_center_y = ((vars.ScreenSize[1] / 2) - self.cy) * -1
			hud.set_text(HeadsUpDisplay.Locations.TOPCENTER, str((math.floor(dist_from_center_x), math.floor(dist_from_center_y))))
			
			"""if self.cx >= self.horizontal:
				self.Clone.rect.centerx = 0.0 - (vars.ScreenSize[0] / 2) - self.cx
			elif self.cx < self.horizontal:
				self.Clone.rect.centerx = self.cx + vars.ScreenSize[0]
			
			if self.cy >= self.vertical:
				self.Clone.rect.centery = 0.0 - (vars.ScreenSize[1] / 2) - self.cy
			elif self.cy < self.vertical:
				self.Clone.rect.centery = self.cy + vars.ScreenSize[1]"""
			
		def draw(self, screen):
			#self.Clone.draw_rect(screen)
			screen.blit(self.image, self.rect)
			#self.Clone.draw(screen)
			vars = Vars()
			for c in self.Clones:
				screen.blit(self.image, c)
				pygame.draw.line(screen, self.linecolor, (c.centerx, c.centery), (vars.ScreenSize[0] / 2, vars.ScreenSize[1] / 2))
				

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
		#self.Asteroids.draw(screen)
		for a in self.Asteroids:
			a.draw(screen)
	
	def init_controls(self):
		pass
