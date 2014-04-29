#!/usr/bin/python

## TODO: add a dynamic event handler to handle custom triggered events
##		eg: on "you died" do function_x()

from Logger import *
import copy
import pygame

class KeyHandler():
	def __init__(self, name=None):
		self.keydown_assignments = {}
		self.keyup_assignments = {}
		self.Name = name
		strname = ""
		if name is not None:
			strname = " with name " + str(name)
		Debug("Initializing a new KeyHandler()" + strname)
	
	def dump_bindings(self):
		print "Keydown assignments"
		for k in self.keydown_assignments:
			print str(k) + ' ' + str(self.keydown_assignments[k]['callback']) + ' ' + str(self.keydown_assignments[k]['args'])
		
		print "Keyup assignments"
		for k in self.keyup_assignments:
			print str(k) + ' ' + str(self.keyup_assignments[k]['callback']) + ' ' + str(self.keyup_assignments[k]['args'])
	
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
			if self.keydown_assignments[key]['args'] != None:
				self.keydown_assignments[key]['callback'](self.keydown_assignments[key]['args'])
			else:
				self.keydown_assignments[key]['callback']()
	
	def do_keyup(self, key):
		""" Execute a key up event's callback. """
		if key in self.keyup_assignments:
			if self.keyup_assignments[key]['args'] != None:
				self.keyup_assignments[key]['callback'](self.keyup_assignments[key]['args'])
			else:
				self.keyup_assignments[key]['callback']()
	
	def clear_all(self):
		""" Reset all events. """
		self.keydown_assignments.clear()
		self.keyup_assignments.clear()
		self.keydown_assignments = {}
		self.keyup_assignments = {}
	
	def copy(self):
		return copy.copy(self)
		
## TODO: dead zone calibration.
## TODO: Joystick factory of sorts.  Do the joystick detection here.
class JoyHandler():
	class RealHandler():
		def __init__(self, name=None):
			self.ButtonHandler = KeyHandler(str(name) + " [auto]")
			"""if pygame.joystick.get_count() <= 0:
				dj = DummyJoy()
				self = dj
				return"""
			
			
			self.hat = []
			self.axes = []
			self.joystick = pygame.joystick.Joystick(0) ## We only care about the first joystick, for now.
			self.joysitck.init()
			self.Name = name
			strname = ""
			
			## FIXME: Are these actually used?
			"""self.Hat = {}
			self.Hat['up'] = False
			self.Hat['down'] = False
			self.Hat['left'] = False
			self.Hat['right'] = False"""
			
			if name is not None:
				strname = " with name " + str(name)
			Debug("Initializing a new JoyHandler()" + strname)
		
		## TODO: store states of hats -- wait, why?
		def update(self):
			## I can't find a controller with more than one hat that isn't the
			## Virtual Boy controller.  We don't care about any more than one in
			## that case.
			if self.joystick.get_numhats() > 0:
				hat = self.joystick.get_hat(0)
				self.hat = hat
			
			if len(self.hat) == 0:
				return


			## Handle the hat directions as buttons.
			for h in (0, 1):			
				if self.hat[0] > 0:
					#self.Hat['right'] = True
					self.ButtonHandler.do_keydown('hatposx')
				else:
					#self.Hat['right'] = False
					self.ButtonHandler.do_keyup('hatposx')
				
				if self.hat[0] < 0:
					#self.Hat['left'] = True
					self.ButtonHandler.do_keydown('hatnegx')
				else:
					#self.Hat['left'] = False
					self.ButtonHandler.do_keyup('hatnegx')
				
				if self.hat[1] > 0:
					#self.Hat['up'] = True
					self.ButtonHandler.do_keydown('hatposy')
				else:
					#self.Hat['up'] = False
					self.ButtonHandler.do_keyup('hatposy')
				
				if self.hat[1] < 0:
					#self.Hat['down'] = True
					self.ButtonHandler.do_keydown('hatnegy')
				else:
					#self.Hat['down'] = False
					self.ButtonHandler.do_keyup('hatnegy')
			
			## Axes on the other hand...
			for i in range(len(self.axes)):
				axis = self.joystick.get_axis(i)
				self.axes[i] = axis
			
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
				Debug("Joydown for " + str(button))
				self.ButtonHandler.do_keydown(button)
		
		def do_joyup(self, button, joy=0):
			if joy == self.joystick.get_id():
				self.ButtonHandler.do_keyup(button)
		
		def add_joydown_handle(self, button, callback, args=None, joy=0):
			if joy == self.joystick.get_id():
				self.ButtonHandler.add_keydown_handle(button, callback, args)
		
		def add_joyup_handle(self, button, callback, args=None, joy=0):
			if joy == self.joystick.get_id():
				self.ButtonHandler.add_keyup_handle(button, callback, args)
		
		def add_joyhold_handle(self, button, callback, joy=0):
			if joy == self.joystick.get_id():
				self.ButtonHandler.add_keyhold_handle(button, callback)
		
		def clear_all(self):
			self.ButtonHandler.clear_all()
		
		def copy(self):
			return copy.copy(self)

#class DummyJoy():
	"""
		Handle joystick events in the event that no joysticks were found.
	"""
	def __init__(self, name=None):
		pygame.joystick.init()
		if pygame.joystick.get_count() > 0:
			rh = RealHandler(name)
			self = rh
			Debug("Found a joystick; using it.")
		else:
			if name is not None:
				self.Name = name + " [DUMMY]"
			else:
				self.Name = "[DUMMY]"
			Debug("Init()'ing a new DummyJoy() object: " + self.Name)
			self.ButtonHandler = KeyHandler(str(self.Name) + " [auto]")

	def update(*arg):
		pass
	
	def get_hat_value(*arg):
		return (0, 0)
	
	def get_axis_value(*arg):
		return 0
	
	def dump_bindings(self):
		Debug("Attempting to dump_bindings() on a DummyJoy() object '" + self.Name + "'; ignoring.")
	
	def do_joydown(*arg):
		pass
	
	def do_joyup(*arg):
		pass
	
	def add_joydown_handle(*arg):
		pass
	
	def add_joyup_handle(*arg):
		pass

	def add_joyhold_handle(*args):
		pass
	
	def clear_all(*args):
		pass

	## Don't bother copying anything.  This might bite me in the ass later...
	def copy(self):
		return self
