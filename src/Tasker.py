#!/usr/bin/python
# coding=utf-8
#
# Copyright (C) 2011 by Coolman & Swiss-MAD
# Copyright (C) 2018-2020 by dream-alpha
#
# In case of reuse of this source code please do not remove this copyright.
#
#	This program is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	For more information on the GNU General Public License see:
#	<http://www.gnu.org/licenses/>.


import random
from enigma import eConsoleAppContainer
from collections import Callable, deque
from pipes import quote
from itertools import izip_longest


class Executioner():

	def __init__(self):
		self.container = eConsoleAppContainer()
		self.container_appClosed_conn = self.container.appClosed.connect(self.runFinished)
		self.script = deque()
		self.associated = deque()
		self.executing = ""

	def isIdle(self):
		return len(self.script) == 0

	def shellExecute(self, script, associated=None, sync=False):
		# Parameters:
		#  script =	single command:   cmd
		#		list of commands: [cmd, cmd]
		#  associated = single callback: callback
		#		single tuple:    (callback, args)
		#		list of tuples:  [(callback),(callback, args),(...)]
		#    callback = function to be executed
		#    args =	single parameter:    arg or (arg) or (a, b) or [a,b]
		#		multiple parameters: arg1, arg2
		#  sync (synchronous callback):
		#    True  = After every command, one callback entry is executed, additionally callbacks will be executed after the last command
		#	     If the callback entry is a tuple or list, all subcallbacks will be executed
		#    False = All callbacks are executed at the end

		if not sync or not isinstance(script, list):
			# Single command execution
			#print("MVC: Tasker: shellExecute: single script: " + str(script))
			self.script.append(script)
			self.associated.append(associated)
		else:
			#print("MVC: Tasker: shellExecute: list script: " + str(script))
			for s, a in izip_longest(script, associated):
				self.script.append(s)
				self.associated.append([a])

		if self.executing == "":
			#print("MVC: Tasker: shellExecute: run script:" + str(self.script))
			self.execCurrent()
		else:
			#print("MVC: Tasker: shellExecute: Run after current execution")
			pass

	def execCurrent(self):
		script = self.script.popleft()
		if script:
			if isinstance(script, list):
				script = '; '.join(script)
			#print("MVC: Tasker: execCurrent: script: " + str(script))
			self.executing = quote(script)
			self.container.execute("sh -c " + self.executing)
			#print("MVC: Tasker: execCurrent: executing: " + self.executing)
		else:
			self.runFinished()

	def runFinished(self, _retval=None):
		associated = self.associated.popleft()
		#print("MVC: Tasker: runFinished: sh exec %s finished, return status = %s" % (self.executing, str(_retval)))
		if associated:
			#P3 for foo, bar, *other in tuple:
			for fargs in associated:
				if isinstance(fargs, (list, tuple)):
					f, args = [e for e in fargs[:1]] + [fargs[1:]]
					if isinstance(f, Callable):
						if args:
							f(*args)
						else:
							f(args)
				else:
					if isinstance(fargs, Callable):
						fargs()

		if self.script:
			# there is more to be executed
			#print("MVC: Tasker: runFinisched: sh exec rebound")
			self.execCurrent()
		else:
			self.executing = ""


class Tasker():

	def __init__(self):
		self.executioners = []
		self.executioners.append(Executioner())
		self.executioners.append(Executioner())
		self.executioners.append(Executioner())

	def shellExecute(self, script, associated=None, sync=False):
		for x in self.executioners:
			if x.isIdle():
				x.shellExecute(script, associated, sync)
				return
		# all were busy, just append to any task list randomly
		self.executioners[random.randint(0, 2)].shellExecute(script, associated, sync)
