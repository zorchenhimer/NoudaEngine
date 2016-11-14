#!/usr/bin/python

import pygame
from lib.Globals import FixPath

## Put health/bullets/etc here?

class HUD:
    def __init__(self, font_path='data/hack-regular.ttf'):
        self.locations = {Locations.TOPLEFT: None, Locations.TOPCENTER: None, Locations.TOPRIGHT: None, Locations.BOTTOMLEFT: None, Locations.BOTTOMCENTER: None, Locations.BOTTOMRIGHT: None}
        ## TODO: make the font a spritesheet and reference it in the blitting process
        self.font = pygame.font.Font(FixPath(font_path), 15)
        self.default_color = (255, 255, 255)
        self.colorkey = (0,0,0)

    def clear_text(self, loc):
        """ Clear all HUD text. """
        if loc & Locations.TOPLEFT:
            self.locations[Locations.TOPLEFT] = None
        if loc & Locations.TOPCENTER:
            self.locations[Locations.TOPCENTER] = None
        if loc & Locations.TOPRIGHT:
            self.locations[Locations.TOPRIGHT] = None
        if loc & Locations.BOTTOMLEFT:
            self.locations[Locations.BOTTOMLEFT] = None
        if loc & Locations.BOTTOMCENTER:
            self.locations[Locations.BOTTOMCENTER] = None
        if loc & Locations.BOTTOMRIGHT:
            self.locations[Locations.BOTTOMRIGHT] = None

    def set_text(self, loc, text):
        """ Set the HUD text for a given HUD location. """
        surfaces = []
        for line in text.split("\n"):
            surfaces.append(self.font.render(line, True, self.default_color).convert_alpha())

        height = 0
        width = 0
        for line in surfaces:
            height += line.get_height()

            if line.get_width() > width:
                width = line.get_width()

        completeSurface = pygame.Surface((width, height), flags=pygame.SRCALPHA)
        completeSurface.fill((0, 0, 0))

        lnum = 0
        if loc & (Locations.TOPLEFT | Locations.BOTTOMLEFT):
            for line in surfaces:
                completeSurface.blit(line, (0, (lnum * line.get_height())))
                lnum += 1

        elif loc & (Locations.TOPCENTER | Locations.BOTTOMCENTER):
            for line in surfaces:
                completeSurface.blit(line, ((width / 2 - line.get_width() / 2), (lnum * line.get_height())))
                lnum += 1

        elif loc & (Locations.TOPRIGHT | Locations.BOTTOMRIGHT):
            for line in surfaces:
                completeSurface.blit(line, ((width - line.get_width()), (lnum * line.get_height())))
                lnum += 1

        self.locations[loc] = completeSurface

    def blit_to_surface(self, destination):
        """
            Blit the HUD to a given surface
        """
        if self.locations[Locations.TOPLEFT]:
            destination.blit(self.locations[Locations.TOPLEFT], (0, 0))
        if self.locations[Locations.TOPCENTER]:
            destination.blit(self.locations[Locations.TOPCENTER], ((destination.get_width() / 2 - self.locations[Locations.TOPCENTER].get_width() / 2), 0))
        if self.locations[Locations.TOPRIGHT]:
            destination.blit(self.locations[Locations.TOPRIGHT], (destination.get_width() - self.locations[Locations.TOPRIGHT].get_width(), 0))
        if self.locations[Locations.BOTTOMLEFT]:
            destination.blit(self.locations[Locations.BOTTOMLEFT], (0, destination.get_height() - self.locations[Locations.BOTTOMLEFT].get_height()))
        if self.locations[Locations.BOTTOMCENTER]:
            destination.blit(self.locations[Locations.BOTTOMCENTER], ((destination.get_width() / 2 - self.locations[Locations.BOTTOMCENTER].get_width() / 2), destination.get_height() - self.locations[Locations.BOTTOMCENTER].get_height()))
        if self.locations[Locations.BOTTOMRIGHT]:
            destination.blit(self.locations[Locations.BOTTOMRIGHT], (destination.get_width() - self.locations[Locations.BOTTOMRIGHT].get_width(), destination.get_height() - self.locations[Locations.BOTTOMRIGHT].get_height()))

class Locations():
    TOPLEFT = 1
    TOPCENTER = 2
    TOPRIGHT = 4
    BOTTOMLEFT = 8
    BOTTOMCENTER = 16
    BOTTOMRIGHT = 32
