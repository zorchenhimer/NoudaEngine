#!/usr/bin/python

import math
import random
from lib.Globals import UnitType, FixPath, Vars
from lib.Logger import *

class MovementPath():
    """
        This class holds all the movement paths for a given object. There are
        three modes: Enter, Dance, and Exit.

        Enter is when the vehicle is entering bounds.  The end point will be
        the start of the dance mode.  Dance mode is automatically triggered.

        Dance is the movement once the vehicle is in bounds.  This mode will
        loop for a given about of time before the exit mode is triggered.

        Exit is the movement after the vehicle's time in play has hit a given
        number.  The first point on this mode should be the first point in the
        dance, otherwise the object will jump.
    """
    class Mode():
        ENTRANCE = 1
        EXIT = 2
        DANCE = 3

    class PathPoint():
        def __init__(self, x, y, time):
            """
                (x, y)
                    X and Y position of the waypoint.
                Time
                    Timestamp of the waypoint in ticks from the begnning of the path.
            """
            self.Pos = (x, y)
            self.Time = time

        def mirror(self):
            (x, y) = self.Pos
            x *= -1
            self.Pos = (x, y)

        def tostring(self):
            return str(self.Pos) + " " + str(self.Time)

    def __init__(self, sprite, PathFile=None):
        self.Entrance = []
        self.Exit = []
        self.Dance = []
        self.CurrentMode = MovementPath.Mode.ENTRANCE
        self.CurrentTick = 0
        self.Sprite = sprite

        if PathFile is not None:
            self.load_path(PathFile)

        self.Static = 0
        self.StaticCountdown = self.Static

    def load_basic_path(self, rand=True):
        vars = Vars()
        startx = vars.ScreenSize.width / 2
        if random:
            startx = random.randint(vars.Bounds.left, vars.Bounds.right)

        self.Entrance = []
        self.Entrance.append(MovementPath.PathPoint((startx, 0), 0))
        self.Entrance.append(MovementPath.PathPoint((startx, vars.ScreenSize.height), 500))
        self.set_mode(MovementPath.Mode.ENTRANCE)

    def dump_paths(self):
        print('Entrance')
        for p in self.Entrance:
            print(p.tostring())

        print('Dance')
        for p in self.Dance:
            print(p.tostring())

        print('Exit')
        for p in self.Exit:
            print(p.tostring())

    def add_waypoint(self, mode, x, y, time):
        waypoint = MovementPath.PathPoint(x, y, time)
        if mode == MovementPath.Mode.ENTRANCE:
            self.Entrance.append(waypoint)
            if self.Static > 1:
                self.Entrance = sorted(self.Entrance, key=lambda point: point.Time)
        elif mode == MovementPath.Mode.EXIT:
            self.Exit.append(waypoint)
            if self.Static > 1:
                self.Exit = sorted(self.Exit, key=lambda point: point.Time)
        elif mode == MovementPath.Mode.DANCE:
            self.Dance.append(waypoint)
            if self.Static > 1:
                self.Dance = sorted(self.Dance, key=lambda point: point.Time)

    def set_mode(self, mode):
        self.CurrentMode = mode

    def load_path(self, filepath, offset=(0, 0), static=1, mirror=False):
        Debug("loading path from file {} using offset {}".format(filepath, offset))
        self.Static = static
        self.StaticCountdown = static
        #filepath = FixPath(filepath)
        Debug("Attempting to load path data from '" + filepath + "'")
        try:
            f = open(filepath, 'r')
        except IOError as msg:
            print("Error opening pathfile " + filepath + "\n\t" + str(msg))
            Warn("Unable to open path file '" + filepath + "': " + str(msg))
            return

        mode = MovementPath.Mode.ENTRANCE
        count = 0
        for line in f:
            line = line.replace('\n', '').replace('\r', '').lower().split(' ')        ## FUCK WINDOWS AND ITS \r!
            #Debug("Split line: " + str(line))
            if len(line) == 1:
                if line[0] == '[enter]':
                    mode = MovementPath.Mode.ENTRANCE
                    count = 0
                    #Debug("Setting path mode to ENTRANCE")
                elif line[0] == '[dance]':
                    mode = MovementPath.Mode.DANCE
                    count = 0
                    #Debug("Setting path mode to DANCE")
                elif line[0] == '[exit]':
                    mode = MovementPath.Mode.EXIT
                    count = 0
                    #Debug("Setting path mode to Exit")
                else:
                    pass
            elif len(line) == 2 or len(line) == 3:
                #try:
                    (posx, posy, time) = (0, 0, 1)
                    if len(line) == 3:
                        (posx, posy, time) = map(int, line)
                        time = int(line[2])
                    else:        ## FIXME: this borked something.  paths are empty in get_position()
                        (posx, posy) = map(int, line)
                        time = static * count

                    if mirror is True:
                        posx *= -1

                    self.add_waypoint(mode, posx + offset[0], posy + offset[1], time)
                #except:
                #    Warn("Line borked in path file! {0!a}".format(line))
                #    pass
            else:
                Info( "ignoring line: " + str(line))
            count += 1

    def kill(self):
        self.Sprite.kill()

    def invert_path_direction(self):
        self.Entrance.reverse()
        self.Dance.reverse()
        self.Exit.reverse()

    def mirror(self):
        for l in [self.Entrance, self.Dance, self.Exit]:
            for p in l:
                p.mirror()

    ## TODO: add a speed setting to this.  Otherwise it's just one waypoint per tick.
    def get_position_sspeed(self):
        modetxt = 'ENTRANCE'
        path = self.Entrance
        if self.CurrentMode == MovementPath.Mode.EXIT:
            path = self.Exit
            modetxt = 'EXIT'
        elif self.CurrentMode == MovementPath.Mode.DANCE:
            path = self.Dance
            modetxt = 'DANCE'

        if len(path) < 1:
            self.kill()
            return (0, 0)

        if self.Static != 0 and self.StaticCountdown > 0:
            self.StaticCountdown -= 1
            return path[0].Pos

        self.StaticCountdown = self.Static

        p = path.pop(0)
        return p.Pos


    ## This shit might not work.
    def get_position_2(self):
        modetxt = 'ENTRANCE'
        path = self.Entrance
        if self.CurrentMode == MovementPath.Mode.EXIT:
            path = self.Exit
            modetxt = 'EXIT'
        elif self.CurrentMode == MovementPath.Mode.DANCE:
            path = self.Dance
            modetxt = 'DANCE'

        if len(path) < 1:
            self.kill()
            return (0, 0)

        lastPoint = path[0]
        ReturnPos = (0, 0)


        ## FIXME: clean up changing between paths
        for p in path:
            if p.Time == self.CurrentTick:
                ReturnPos = p.Pos
                break

            elif p.Time < self.CurrentTick:
                lastPoint = p

            elif p.Time > self.CurrentTick:

                distx = p.Pos[0] - lastPoint.Pos[0]
                disty = p.Pos[1] - lastPoint.Pos[1]
                tickdiff = p.Time - lastPoint.Time

                if tickdiff > 0:
                    pertickx = (distx / (tickdiff * 1.0))
                    perticky = (disty / (tickdiff * 1.0))
                else:
                    pertickx = 1
                    perticky = 1

                lastT = self.CurrentTick - lastPoint.Time    #ticks since last waypoint

                ## Difference between the current tick, and the next waypoint's tick
                secondtick = p.Time - self.CurrentTick

                ## Find the new (X, Y) for the sprite
                x = math.floor(pertickx * lastT)
                y = math.floor(perticky * lastT)

                ReturnPos = (lastPoint.Pos[0] + x, lastPoint.Pos[1] + y)
                break

            if self.CurrentTick > path[-1].Time:
                ## Start over if we found the last waypoint in the Dance routine
                ## TODO: make a dance last X loops
                if self.CurrentMode == MovementPath.Mode.DANCE:
                    self.CurrentTick = 0
                    ReturnPos = path[0].Pos
                    break
                elif self.CurrentMode == MovementPath.Mode.ENTRANCE:
                    self.CurrentTick = 0
                    if len(self.Dance) < 1:
                        if len(self.Exit) < 1:
                            self.Sprite.kill()
                            return (0, 0)
                        else:
                            self.CurrentMode = MovementPath.Mode.EXIT
                            ReturnPos = self.Exit[0].pos
                    else:
                        self.CurrentMode = MovementPath.Mode.DANCE
                        ReturnPos = self.Dance[0].Pos
                    break

        self.CurrentTick += 1
        return ReturnPos

    ## This shit might not work.
    def get_position(self):
        modetxt = 'ENTRANCE'
        path = self.Entrance
        if self.CurrentMode == MovementPath.Mode.EXIT:
            path = self.Exit
            modetxt = 'EXIT'
        elif self.CurrentMode == MovementPath.Mode.DANCE:
            path = self.Dance
            modetxt = 'DANCE'
        if len(path) < 1:
            self.kill()
            return (0, 0)

        lastPoint = path[0]
        ReturnPos = (0, 0)


        ## FIXME: clean up changing between paths
        for p in path:
            #Debug("p.time: " + str(p.Time))
            if p.Time == self.CurrentTick:
                ReturnPos = p.Pos
                break

            elif p.Time < self.CurrentTick:
                lastPoint = p

            elif p.Time > self.CurrentTick:

                distx = p.Pos[0] - lastPoint.Pos[0]
                disty = p.Pos[1] - lastPoint.Pos[1]
                tickdiff = p.Time - lastPoint.Time

                if tickdiff > 0:
                    pertickx = (distx / (tickdiff * 1.0))
                    perticky = (disty / (tickdiff * 1.0))
                else:
                    pertickx = 1
                    perticky = 1

                lastT = self.CurrentTick - lastPoint.Time    #ticks since last waypoint

                ## Difference between the current tick, and the next waypoint's tick
                secondtick = p.Time - self.CurrentTick

                ## Find the new (X, Y) for the sprite
                x = math.floor(pertickx * lastT)
                y = math.floor(perticky * lastT)

                ReturnPos = (lastPoint.Pos[0] + x, lastPoint.Pos[1] + y)
                break

            if self.CurrentTick > path[-1].Time:
                ## Start over if we found the last waypoint in the Dance routine
                ## TODO: make a dance last X loops
                if self.CurrentMode == MovementPath.Mode.DANCE:
                    self.CurrentTick = 0
                    ReturnPos = path[0].Pos
                    break
                elif self.CurrentMode == MovementPath.Mode.ENTRANCE:
                    self.CurrentTick = 0
                    if len(self.Dance) < 1:
                        if len(self.Exit) < 1:
                            self.Sprite.kill()
                            return (0, 0)
                        else:
                            self.CurrentMode = MovementPath.Mode.EXIT
                            ReturnPos = self.Exit[0].pos
                    else:
                        self.CurrentMode = MovementPath.Mode.DANCE
                        ReturnPos = self.Dance[0].Pos
                    break

        self.CurrentTick += 1
        return ReturnPos
