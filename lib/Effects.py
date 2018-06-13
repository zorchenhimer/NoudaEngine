#!/usr/bin/python

import pygame
from lib.Globals import LoadImage, UnitType

class Explosion(pygame.sprite.Sprite):
    def __init__(self, unittype, pos, fuse=10):
        pygame.sprite.Sprite.__init__(self)
        self.Fuse = fuse
        self.image = None

        if unittype == UnitType.PLAYER:
            self.image = LoadImage('png/Lasers/lasergreenshot.png')
        else:
            self.image = LoadImage('png/Lasers/laserredshot.png')

        self.SpriteImage = self.image
        self.rect = self.image.get_rect()
        self.rect.centerx = pos[0]
        self.rect.centery = pos[1]

        if self.Fuse > 0:
            self.AlphaStep = 255 / self.Fuse
        else:
            self.AlphaStep = 127

    def update(self):
        if self.Fuse > 0:
            self.Fuse -= 1
            self.image = self.SpriteImage.copy()
            self.image.fill((255, 255, 255, (self.AlphaStep * self.Fuse)), None, pygame.BLEND_RGBA_MULT)
        else:
            self.kill()
