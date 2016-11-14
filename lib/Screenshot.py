#!/usr/bin/python

import pygame
import time
import os
import lib.EventHandler
from lib.Globals import Info

class Screenshot():
    def __init__(self):
        if not os.path.isdir('screenshots'):
            os.mkdir('screenshots')
        
        self.Prefix = 'screenshots/' + str(int(time.time())) + '_'
        self.Counter = 0
        
    def TakeShot(self, screen):
        filename = self.Prefix + str(self.Counter) + '.png'
        pygame.image.save(screen, filename)
        self.Counter += 1
        Info('Screenshot saved as ' + filename)
