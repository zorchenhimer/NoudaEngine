#!/usr/bin/python

import math
import pygame
from lib.Globals import UnitType, Debug, Vars, LoadImage
import lib.Effects

class Projectile(pygame.sprite.Sprite):
    """ All projectiles will inherit this class for a basic projectile. """
    def __init__(self, d=None, l=-1, offset=0):
        pygame.sprite.Sprite.__init__(self)
        self.Degrees = d
        self.Speed = 6        # Movement per tick
        self.Life = l        ## Anything higher than -1 will determine how many
                            ## ticks the projectile is alive.
        self.Offset = offset    # Number of ticks to skip when calculating the start position.

        self.image = None
        self.rect = None

        self.realX = 0.0
        self.realY = 0.0

    def calculate_path(self):
        if self.Degrees is None:
            self.Degrees = 0.0

        self.Radian = (self.Degrees - 90.0) * (math.pi / 180.0)

        ## Distance the projectile travels per tick, given the angle above.
        self.StepX = self.Speed * math.cos(self.Radian)
        self.StepY = self.Speed * math.sin(self.Radian)

        while self.Offset > 0:
            self.rect.x += self.StepX
            self.rect.y += self.StepY
            self.Offset -= 1

        while self.Offset < 0:
            self.rect.x -= self.StepX
            self.rect.y -= self.StepY
            self.Offset += 1

        Debug('Recalculated vector: ({x}, {y})'.format(x=self.StepX, y=self.StepY))

    def update(self, nobounds=False):
        ## Move the projectile keeping in mind the direction.
        self.rect.x += self.StepX
        self.rect.y += self.StepY

        if self.Life > -1:
            if self.Life == 0:
                self.kill()
            else:
                self.Life -= 1

    def check_bounds(self):
        vars = Vars()
        if pygame.display.get_surface().get_rect().contains(self.rect):
            return True
        return False

class Bullet(Projectile):
    def __init__(self, t, x, y, d=None, l=-1, offset=0):
        Projectile.__init__(self, d, l, offset)

        self.Type = t

        ## Defaults given the unit type that fired the projectile.
        if self.Degrees == None:
            if self.Type == UnitType.PLAYER:
                self.Degrees = 0.0
            elif self.Type == UnitType.ENEMY:
                self.Degrees = 180.0
            else:
                self.Degrees = 90.0

        ## Load the correct image.
        if self.Type == UnitType.PLAYER:
            self.image = pygame.transform.rotozoom(LoadImage('png/Lasers/laserGreen02.png'), (self.Degrees * -1), 1)
            self.Speed = 15
        else:
            self.image = pygame.transform.rotozoom(LoadImage('png/Lasers/laserRed02.png'), (self.Degrees * -1), 1)
            self.Speed = 15

        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y

        self.calculate_path()

    def update(self):
        if not self.check_bounds():
            self.kill()
        else:
            Projectile.update(self)

class BulletBomb(Bullet):
    def __init__(self, t, x, y, group, d=0, l=90):
        Bullet.__init__(self, t, x, y, d, l)
        self.Fuse = 20
        self.Speed = 1
        self.Group = group

    def detonate(self):
        shrapnel = 8
        for n in range(shrapnel):
            self.Group.add(BulletBomb(self.Type, self.rect.centerx, self.rect.centery, self.Group, (n * (360.0 / shrapnel)), self.Life - 20))
        self.Group.add(Effects.Explosion(self.Type, (self.rect.centerx, self.rect.centery)))
        self.kill()

    def update(self):
        if self.Fuse > 0:
            self.Fuse -= 1
            Bullet.update(self)
        else:
            self.detonate()
