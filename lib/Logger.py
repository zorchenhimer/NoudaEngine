#!/usr/bin/python

"""
    Handles all logging stuffs.
"""

#from Globals import FixPath
import time

__all__ = ["Debug", "Info", "Warn", "LogLevel", "SetLogLevel", "SetPrintLevel"]

class LogLevel():
    SILENT = 0
    WARN = 1        ## Default
    INFO = 2
    DEBUG = 3

## This class is not imported by default
class Logger():
    """
        This is what does all the brunt work.
    """
    class _InnerClass():
        def __init__(self, level=None):
            #self.__log_file = FixPath('debug.log')
            self.__log_file = 'debug.log'
            self.__log_level = LogLevel.WARN
            self.__print_level = LogLevel.DEBUG

            if level is not None:
                if type(level) is not int:
                    raise TypeError('\'level\' type is not an int! Found instead: ' + str(type(level)))
                if level > 3 or level < 0:
                    raise IndexError('\'level\' is out of range! Found: ' + str(level))

            if self.__log_level is not LogLevel.SILENT:
                f = open(self.__log_file, 'w')
                f.close()

        def WriteToLog(self, message, level):
            if type(message) is not str:
                raise TypeError('message in WriteToLog is not a string! Found instead: ' + str(type(message)))

            t = '[{n}]'.format(n=time.time())

            prefix = '[WARN]'
            if level == LogLevel.INFO:
                prefix = '[INFO]'
            elif level == LogLevel.DEBUG:
                prefix = '[DEBUG]'

            if self.__print_level >= level:
                print(t + prefix + ' ' + message)

            if self.__log_level >= level:
                f = open(self.__log_file, 'a')
                f.write(t + prefix + ' ' + message + "\n")
                f.close()

        def SetLogLevel(self, level):
            if type(level) is not int:
                raise TypeError('\'level\' type is not an int! Found instead: ' + str(type(level)))
            if level > LogLevel.DEBUG or level < LogLevel.SILENT:
                raise IndexError('\'level\' is out of range! Found: ' + str(level))

            self.__log_level = level

        def SetPrintLevel(self, level):
            if type(level) is not int:
                raise TypeError('\'level\' type is not an int! Found instead: ' + str(type(level)))
            if level > LogLevel.DEBUG or level < LogLevel.SILENT:
                raise IndexError('\'level\' is out of range! Found: ' + str(level))

            self.__print_level = level

        def GetLogLevelStr(self):
            if self.__log_level == 0:
                return 'SILENT'
            elif self.__log_level == 1:
                return 'WARN'
            elif self.__log_level == 2:
                return 'INFO'
            else:    ## We don't want to blow up here, so don't raise().
                return 'DEBUG'

        def GetLogLevelStr(self):
            if self.__print_level == 0:
                return 'SILENT'
            elif self.__print_level == 1:
                return 'WARN'
            elif self.__print_level == 2:
                return 'INFO'
            else:    ## We don't want to blow up here, so don't raise().
                return 'DEBUG'

        def GetLogLevel(self):
            return self.__log_level

        def GetPrintLevel(self):
            return self.__print_level

    __instance = None

    def __init__(self, level=None):
        if Logger.__instance == None:
            Logger.__instance = Logger._InnerClass(level)

        self.__dict__['_Singleton_instance'] = Logger.__instance

    def __getattr__(self, attr):
        return getattr(self.__instance, attr)

    def __setattr__(self, attr, value):
        return setattr(self.__instance, attr, value)

## Import these things; either explicitly or via `from Logger import *`
def Debug(message):
    l = Logger()
    l.WriteToLog(message, LogLevel.DEBUG)

def Info(message):
    l = Logger()
    l.WriteToLog(message, LogLevel.INFO)

def Warn(message):
    l = Logger()
    l.WriteToLog(message, LogLevel.WARN)

def SetLogLevel(level):
    l = Logger()
    if type(level) is str:
        if level.lower() == 'silent':
            l.SetLogLevel(LogLevel.SILENT)
        elif level.lower() == 'warn':
            l.SetLogLevel(LogLevel.WARN)
        elif level.lower() == 'info':
            l.SetLogLevel(LogLevel.INFO)
        elif level.lower() == 'debug':
            l.SetLogLevel(LogLevel.DEBUG)
        else:
            raise RuntimeError("level string is incorrect.")

    elif type(level) is int:
        if level >= LogLevel.SILENT and level <= LogLevel.DEBUG:
            l.SetLogLevel(level)
        else:
            raise IndexError("level is out of range.")

    else:
        raise TypeError("Unexpected type: " + str(type(level)))

def SetPrintLevel(level):
    l = Logger()
    if type(level) is str:
        if level.lower() == 'silent':
            l.SetPrintLevel(LogLevel.SILENT)
        elif level.lower() == 'warn':
            l.SetPrintLevel(LogLevel.WARN)
        elif level.lower() == 'info':
            l.SetPrintLevel(LogLevel.INFO)
        elif level.lower() == 'debug':
            l.SetPrintLevel(LogLevel.DEBUG)
        else:
            raise RuntimeError("level string is incorrect.")

    elif type(level) is int:
        if level >= LogLevel.SILENT and level <= LogLevel.DEBUG:
            l.SetPrintLevel(level)
        else:
            raise IndexError("level is out of range.")

    else:
        raise TypeError("Unexpected type: " + str(type(level)))
