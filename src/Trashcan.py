#!/usr/bin/python
# coding=utf-8
#
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


import os
import time
from Components.config import config
from DelayTimer import DelayTimer
from FileCache import FileCache, FILE_IDX_PATH, FILE_IDX_TYPE
from FileOps import FileOps, FILE_OP_DELETE
from Bookmarks import getBookmarks, getHomeDir
from FileUtils import createDirectory
from FileListUtils import createFileList


RC_TRASHCAN_CREATED = 0
RC_TRASHCAN_CREATE_DIR_FAILED = 1


instance = None


class Trashcan(FileOps):

	def __init__(self):
		FileOps.__init__(self)
		self.__schedulePurge()

	@staticmethod
	def getInstance():
		global instance
		if instance is None:
			instance = Trashcan()
		return instance

	def reloadList(self, path):
		print("MVC-I: Trashcan: reloadList: no reload necessary for path: %s" % path)

	def __schedulePurge(self):
		if config.plugins.moviecockpit.trashcan_enable.value and config.plugins.moviecockpit.trashcan_clean.value:
			# recall function in 24 hours
			seconds = 24 * 60 * 60
			DelayTimer(1000 * seconds, self.__schedulePurge)
			# execute trash cleaning
			DelayTimer(5000, self.purgeTrashcan)
			print("MVC-I: Trashcan: scheduleCleanup: next trashcan cleanup in %s minutes" % (seconds / 60))

	def enableTrashcan(self):
		print("MVC-I: Trashcan: enableTrashcan")
		config.plugins.moviecockpit.trashcan_enable.value = False
		rc = RC_TRASHCAN_CREATE_DIR_FAILED
		for bookmark in getBookmarks():
			path = bookmark + "/trashcan"
			if FileCache.getInstance().exists(path):
				rc = RC_TRASHCAN_CREATED
				config.plugins.moviecockpit.trashcan_enable.value = True
			else:
				rc = createDirectory(path)
				if not rc:
					print("MVC-I: Trashcan: enableTrashcan: successful: %s" % path)
					FileCache.getInstance().loadDatabase([path], sync=True)
					config.plugins.moviecockpit.trashcan_enable.value = True
				else:
					print("MVC-E: Trashcan: enableTrashcan: failed: %s" % path)
					config.plugins.moviecockpit.trashcan_enable.value = False
					break
		return rc

	def purgeTrashcan(self):
		print("MVC-I: Trashcan: purgeTrashcan")
		file_ops_list = []
		now = time.localtime()
		filelist = createFileList(getHomeDir() + "/trashcan")
		for afile in filelist:
			path = afile[FILE_IDX_PATH]
			filetype = afile[FILE_IDX_TYPE]
			if os.path.exists(path):
				if now > time.localtime(os.stat(path).st_mtime + 24 * 60 * 60 * int(config.plugins.moviecockpit.trashcan_retention.value)):
					#print("MVC: Trashcan: purgeTrashcan: path: " + path)
					file_ops_list.append((FILE_OP_DELETE, path, None, filetype))
		if file_ops_list:
			self.execFileOpsNoProgress(file_ops_list)
		print("MVC-I: Trashcan: purgeTrashcan: deleted %s files" % len(file_ops_list))
