#!/usr/bin/python
# coding=utf-8
#
# Copyright (C) 2018-2019 by dream-alpha
#:
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
#

import os
from __init__ import _
from Components.config import config
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.Button import Button
from Components.Slider import Slider
from Bookmarks import Bookmarks

class FileProgress(Screen, Bookmarks):

	def __init__(self, session, return_path):
		#print("MVC: FileProgress: __init__")
		Bookmarks.__init__(self)
		Screen.__init__(self, session)

		self["slider1"] = Slider(0, 100)
		self["slider2"] = Slider(0, 100)

		self["status"] = Label("")
		self["name"] = Label("")
		self["operation"] = Label("")

		self["key_red"] = Button(_("Cancel"))
		self["key_green"] = Button(_("Close"))
		self["key_yellow"] = Button("")
		self["key_blue"] = Button(_("Hide"))

		self["key_red"].show()
		self["key_blue"].show()
		self["key_green"].hide()

		self["actions"] = ActionMap(
			["OkCancelActions", "ColorActions"],
			{"ok": self.exit, "cancel": self.cancel, "red": self.cancel, "green": self.exit, "yellow": self.noop, "blue": self.toggleHide}
		)

		self.return_path = return_path
		self.execution_list = []
		self.total_files = 0
		self.current_files = 0
		self.file_progress = 0
		self.file_name = ""
		self.status = ""
		self.request_cancel = False
		self.cancelled = False
		self.hidden = False

	def noop(self):
		return

	def cancel(self):
		if self.hidden:
			#print("MVC: FileProgress: cancel: unhide")
			self.toggleHide()
		else:
			if self.cancelled or (self.current_files > self.total_files):
				#print("MVC: FileProgress: cancel: exit")
				self.exit()
			else:
				#print("MVC: FileProgress: cancel: trigger")
				self.request_cancel = True
				self["key_red"].hide()
				self["key_blue"].hide()
				self["key_green"].hide()
				self.status = _("Cancelling, please wait") + " ..."

	def exit(self):
		if self.hidden:
			#print("MVC: FileProgress: unhide: trigger")
			self.toggleHide()
		else:
			if self.cancelled or (self.current_files > self.total_files):
				#print("MVC: FileProgress: exit: close")
				self.close()

	def toggleHide(self):
		if self.hidden:
			self.hidden = False
			dimm = config.av.osd_alpha.value
		else:
			self.hidden = True
			dimm = 0

		f = open("/proc/stb/video/alpha", "w")
		f.write("%i" % dimm)
		f.close()

	def reloadList(self, path):
		print("MVC-E: FileProgress: reloadList: path: %s" % path)

	def updateProgress(self):
		#print("MVC: MovieCoverDownloadProgress: updateProgress: file_name: %s, current_files: %s, total_files: %s, status: %s" % (self.file_name, self.current_files, self.total_files, self.status))
		current_files = self.current_files if self.current_files <= self.total_files else self.total_files
		msg = _("Downloading") + ": " + str(current_files) + " " + _("of") + " " + str(self.total_files) + " ..."
		self["operation"].setText(msg)
		self["name"].setText(self.file_name)
		percent_complete = int(round(float(self.current_files - 1) / float(self.total_files) * 100)) if self.total_files > 0 else 0
		self["slider1"].setValue(percent_complete)
		self["status"].setText(self.status)

	def completionStatus(self):
		return _("Done")

	def doFileOp(self, _entry):
		# is overridden in parent class
		return

	def nextFileOp(self):
		#print("MVC: FileProgress: nextFileOp")

		self.current_files += 1
		if self.request_cancel and (self.current_files <= self.total_files):
			self.current_files -= 1
			if self.hidden:
				self.toggleHide()
			self["key_red"].hide()
			self["key_blue"].hide()
			self["key_green"].show()
			self.status = _("Cancelled")
			self.cancelled = True
			self.updateProgress()
		else:
			if self.execution_list:
				entry = self.execution_list.pop(0)
				self.status = _("Please wait") + " ..."
				self.doFileOp(entry)
			else:
				#print("MVC: FileProgress: nextFileOp: done.")
				if self.hidden:
					self.toggleHide()
				self["key_red"].hide()
				self["key_blue"].hide()
				self["key_green"].show()
				if self.cancelled:
					self.status = _("Cancelled")
				else:
					self.status = self.completionStatus()
				self.updateProgress()
				if self.return_path is not None:
					self.reloadList(os.path.dirname(self.return_path))
