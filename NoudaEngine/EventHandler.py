#!/usr/bin/python

## TODO: add a dynamic event handler to handle custom triggered events
##		eg: on "you died" do function_x()

from Logger import *
import copy
import pygame
import random

class KeyHandler():
	def __init__(self, name=None):
		self.keydown_assignments = {}
		self.keyup_assignments = {}
		self.Name = name
		strname = ""
		
		rand = random.Random()
		self.randID = rand.randint(0, 100000)
		
		if name is not None:
			strname = " with name " + str(name)		
		Debug("Initializing a new KeyHandler()" + strname + " [" + str(self.randID) + "]")
	
	def dump_bindings(self):
		Debug(" === Keydown assignments === ")
		for k in self.keydown_assignments:
			Debug(str(k) + ' ' + str(self.keydown_assignments[k]['callback']) + ' ' + str(self.keydown_assignments[k]['args']))
		
		Debug(" === Keyup assignments === ")
		for k in self.keyup_assignments:
			Debug(str(k) + ' ' + str(self.keyup_assignments[k]['callback']) + ' ' + str(self.keyup_assignments[k]['args']))
	
	def add_keydown_handle(self, key, callback, args=None):
		""" Add a handler for a given key down event. args are passed to the callback function. """
		self.keydown_assignments[key] = {'callback': callback, 'args': args}
	
	def add_keyup_handle(self, key, callback, args=None):
		""" Add a handler for a given key up event. args are passed to the callback function. """
		self.keyup_assignments[key] = {'callback': callback, 'args': args}
	
	def add_keyhold_handle(self, key, callback):
		""" Add both key up and key down handlers for the given event. """
		## Callbacks must take exactly one argument that evaluates to True or False
		self.add_keydown_handle(key, callback, True)
		self.add_keyup_handle(key, callback, False)
	
	def do_keydown(self, key):
		""" Execute a key down event's callback. """
		if key in self.keydown_assignments:
#			Debug("Keydown for " + str(key))
			if self.keydown_assignments[key]['args'] != None:
				self.keydown_assignments[key]['callback'](self.keydown_assignments[key]['args'])
			else:
				self.keydown_assignments[key]['callback']()
#		else:
#			Debug("[" + self.Name +"][" + str(self.randID) + "] Unbound keydown: " + str(key))
	
	def do_keyup(self, key):
		""" Execute a key up event's callback. """
		if key in self.keyup_assignments:
			if self.keyup_assignments[key]['args'] != None:
				self.keyup_assignments[key]['callback'](self.keyup_assignments[key]['args'])
			else:
				self.keyup_assignments[key]['callback']()
#		else:
#			Debug("[" + self.Name +"][" + str(self.randID) + "] Unbound keyup: " + str(key))
	
	def clear_all(self):
		""" Reset all events. """
		self.keydown_assignments.clear()
		self.keyup_assignments.clear()
		self.keydown_assignments = {}
		self.keyup_assignments = {}
	
	def copy(self):
		return copy.copy(self)

## TODO: Analogue sticks
class JoyHandler():
	"""
		Handle all joystick input for the given context
	"""
	class RealHandler():
		class MrHat():
			"""
				Update the values of the hat.  Making this a class gives the
				possibility of supporting more than one hat.
			"""
			def __init__(self, handler):
				self.__PosX = False
				self.__PosY = False
				self.__NegX = False
				self.__NegY = False
				self.__Handler = handler
			
			def dump_states(self, hat):
				Debug("PosX:\t" + str(self.__PosX))
				Debug("PosY:\t" + str(self.__PosY))
				Debug("NegX:\t" + str(self.__NegX))
				Debug("NegY:\t" + str(self.__NegY))
				Debug("hat[0]: " + str(hat[0]))
				Debug("hat[1]: " + str(hat[1]))
			
			def update(self, hat):
				## Left/Right Keyup
				if hat[0] == 0:
					## Right
					if self.__PosX is not False:
						self.__PosX = False
						self.__Handler.do_keyup('hatposx')
					## Left
					if self.__NegX is not False:
						self.__NegX = False
						self.__Handler.do_keyup('hatnegx')
				
				## Right Keydown
				if hat[0] == 1 and self.__PosX is not True:
					if self.__NegX is True:
						self.__NegX = False
						self.__Handler.do_keyup('hatnegx')
					
					self.__PosX = True
					self.__Handler.do_keydown('hatposx')
				
				## Left Keydown
				if hat[0] == -1 and self.__NegX is not True:
					if self.__PosX is True:
						self.__PosX = False
						self.__Handler.do_keyup('hatposx')
						
					self.__NegX = True
					self.__Handler.do_keydown('hatnegx')
				
				## Up/Down Keyup
				if hat[1] == 0:
					## Up
					if self.__PosY is not False:
						self.__PosY = False
						self.__Handler.do_keyup('hatposy')
					## Down
					if self.__NegY is not False:
						self.__NegY = False
						self.__Handler.do_keyup('hatnegy')
				
				## Up Keydown
				if hat[1] == 1 and self.__PosY is not True:
					if self.__NegY is True:
						self.__NegY = False
						self.__Handler.do_keyup('hatnegy')
						
					self.__PosY = True
					self.__Handler.do_keydown('hatposy')
				
				## Down Keydown
				if hat[1] == -1 and self.__NegY is not True:
					if self.__PosY is True:
						self.__PosY = False
						self.__Handler.do_keyup('hatposy')
						
					self.__NegY = True
					self.__Handler.do_keydown('hatnegy')
				
		def __init__(self, rID, name=None):
			self.ButtonHandler = KeyHandler(str(name) + " [auto]")
			
			self.hat = JoyHandler.RealHandler.MrHat(self.ButtonHandler)
			self.axes = []
			self.joystick = pygame.joystick.Joystick(0) ## We only care about the first joystick, for now.
			self.joystick.init()
			self.Name = name
			strname = ""
			self.randID = rID
			
			if name is not None:
				strname = " with name " + str(name)
			Debug("Initializing a new JoyHandler()" + strname + " [" + str(self.randID) + "]")
		
		def update(self):
			## I can't find a controller with more than one hat that isn't the
			## Virtual Boy controller.  We don't care about any more than one in
			## that case.
			if self.joystick.get_numhats() > 0:
				self.hat.update(self.joystick.get_hat(0))
			
			## Axes on the other hand...
			for i in range(len(self.axes)):
				axis = self.joystick.get_axis(i)
				self.axes[i] = axis
		
		def dump_hats(self):
			if self.joystick.get_numhats() > 0:
				h = self.joystick.get_hat(0)
				self.hat.dump_states(h)
		
		def get_hat_value(self, hat):
			return self.hat
		
		## FIXME: make this better with error checking/catching.
		def get_axis_value(self, axis):
			if len(self.axes) == 0 or len(self.axis) - 1 < axis or axis < 0:
				return 0
			return self.axes[axis]
		
		## Because why write shit twice?
		def dump_bindings(self):
			self.ButtonHandler.dump_bindings()
		
		def do_joydown(self, button, joy=0):
			if joy == self.joystick.get_id():
				self.ButtonHandler.do_keydown(button)
		
		def do_joyup(self, button, joy=0):
			if joy == self.joystick.get_id():
				self.ButtonHandler.do_keyup(button)
		
		def add_joydown_handle(self, button, callback, args=None, joy=0):
			if joy == self.joystick.get_id():
				#Debug("[" + self.Name + "] Adding joydown for " + str(button) + " with callback " + str(callback))
				self.ButtonHandler.add_keydown_handle(button, callback, args)
		
		def add_joyup_handle(self, button, callback, args=None, joy=0):
			if joy == self.joystick.get_id():
				#Debug("[" + self.Name + "] Adding joyup for " + str(button) + " with callback " + str(callback))
				self.ButtonHandler.add_keyup_handle(button, callback, args)
		
		def add_joyhold_handle(self, button, callback, joy=0):
			if joy == self.joystick.get_id():
				self.ButtonHandler.add_keyhold_handle(button, callback)
		
		def clear_all(self):
			self.ButtonHandler.clear_all()
		
		def copy(self):
			return copy.copy(self)
	
	"""
		Wrapper below.  If we find a joystick, use JoyHandler.RealHandler().
		Otherwise quietly ignore all joystick actions.
	"""
	def __init__(self, name=None):
		pygame.joystick.init()
		self.real_handle = None
		rand = random.Random()
		self.randID = rand.randint(0, 100000)
		
		if pygame.joystick.get_count() > 0:
			self.real_handle = JoyHandler.RealHandler(self.randID, name)
			Debug("Found a joystick; using it.")
		else:
			if name is not None:
				self.Name = name + " [DUMMY]"
			else:
				self.Name = "[DUMMY]"
			Debug("Init()'ing a new DummyJoy() object: " + self.Name)
			self.ButtonHandler = KeyHandler(str(self.Name) + " [auto]")

	def update(self):
		if self.real_handle is not None:
			return self.real_handle.update()
		pass
	
	def get_hat_value(self, hat):
		if self.real_handle is not None:
			return self.real_handle.get_hat_value(hat)
		return (0, 0)
	
	def get_axis_value(self, axis):
		if self.real_handle is not None:
			return self.real_handle.get_axis_value(axis)
		return 0
	
	def dump_hats(self):
		if self.real_handle is not None:
			self.real_handle.dump_hats()
	
	def dump_bindings(self):
		if self.real_handle is not None:
			return self.real_handle.dump_bindings()
		else:
			Debug("Attempting to dump_bindings() on a DummyJoy() object '" + self.Name + "'; ignoring.")
	
	def do_joydown(self, button, joy=0):
		if self.real_handle is not None:
			self.real_handle.do_joydown(button, joy)
	
	def do_joyup(self, button, joy=0):
		if self.real_handle is not None:
			self.real_handle.do_joyup(button, joy)
	
	def add_joydown_handle(self, button, callback, args=None, joy=0):
		if self.real_handle is not None:
			self.real_handle.add_joydown_handle(button, callback, args,)
	
	def add_joyup_handle(self, button, callback, args=None, joy=0):
		if self.real_handle is not None:
			self.real_handle.add_joyup_handle(button, callback, args, joy)

	def add_joyhold_handle(self, button, callback, joy=0):
		if self.real_handle is not None:
			self.real_handle.add_joyhold_handle(button, callback, joy)
	
	def clear_all(self):
		if self.real_handle is not None:
			self.real_handle.clear_all()

	def copy(self):
		if self.real_handle is not None:
			return copy.copy(self)
		return self
