#!/usr/bin/python
# encoding: utf-8
#
# Copyright (C) 2018-2019 by dream-alpha
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
#

import os
from datetime import datetime
from Components.config import config
from enigma import eServiceReference
from MediaTypes import plyDVB, plyM2TS, plyDVD, sidDVB, sidDVD, sidM2TS
from FileCache import FileCache, FILE_TYPE_DIR, FILE_IDX_TYPE, FILE_IDX_NAME, FILE_IDX_DATE, FILE_IDX_PATH, FILE_IDX_EXT
from Bookmarks import Bookmarks

class FileListUtils(Bookmarks, object):

	def getEntry4Index(self, filelist, index):
		return filelist[index]

	def getEntry4Path(self, filelist, path):
		list_entry = None
		for entry in filelist:
			if entry and entry[FILE_IDX_PATH] == path:
				list_entry = entry
				break
		return list_entry

	def getIndex4Path(self, filelist, path):
		index = -1
		for i, entry in enumerate(filelist):
			if entry and entry[FILE_IDX_PATH] == path:
				index = i
				break
		return index

	def getService4Path(self, filelist, path):
		service = None
		for entry in filelist:
			if entry and entry[FILE_IDX_PATH] == path:
				service = self.__getService(path, entry[FILE_IDX_NAME], entry[FILE_IDX_EXT])
				break
		return service

	def createFileList(self, path):
		filelist = FileCache.getInstance().getFileList([path])
		if config.MVC.directories_show.value:
			filelist += FileCache.getInstance().getDirList([path])
		return filelist

	def createCustomList(self, path):
		#print("MVC: MovieSelection: createCustomList: path: %s" % path)
		custom_list = []
		if path not in self.getBookmarks():
			custom_list.append(FileCache.getInstance().getFile(os.path.join(path, "..")))
		else:  # path is a bookmark
			if config.MVC.trashcan_enable.value and config.MVC.trashcan_show.value:
				custom_list.append(FileCache.getInstance().getFile(path + "/trashcan"))
		#print("MVC: MovieSelection: createCustomList: custom_list: " + str(custom_list))
		return custom_list

	def sortList(self, sort_list, sort):

		def date2ms(date_string):
			return int(datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S").strftime('%s')) * 1000

		filetype_list = [] if config.MVC.directories_ontop.value else [FILE_TYPE_DIR]
		# This will find all unsortable items
		tmp_list = [i for i in sort_list if i and i[FILE_IDX_TYPE] in filetype_list or i[FILE_IDX_NAME] == ".."]
		# Extract list items to be sorted
		sort_list = [i for i in sort_list if i and i[FILE_IDX_TYPE] not in filetype_list and i[FILE_IDX_NAME] != ".."]
		# Always sort via extension and sorttitle
		tmp_list.sort(key=lambda x: (x[FILE_IDX_TYPE], x[FILE_IDX_NAME].lower()))

		mode, order = sort

		if mode == "D": # Date sort
			if not order:
				sort_list.sort(key=lambda x: (x[FILE_IDX_DATE], x[FILE_IDX_NAME].lower()), reverse=True)
			else:
				sort_list.sort(key=lambda x: (x[FILE_IDX_DATE], x[FILE_IDX_NAME].lower()))

		elif mode == "A": # Alpha sort
			if not order:
				sort_list.sort(key=lambda x: (x[FILE_IDX_NAME].lower(), -date2ms(x[FILE_IDX_DATE])))
			else:
				sort_list.sort(key=lambda x: (x[FILE_IDX_NAME].lower(), x[FILE_IDX_DATE]), reverse=True)

		return tmp_list + sort_list

	def __getService(self, path, name="", ext=None):
		if ext in plyDVB:
			service = eServiceReference(sidDVB, 0, path)
		elif ext in plyDVD:
			service = eServiceReference(sidDVD, 0, path)
		elif ext in plyM2TS:
			service = eServiceReference(sidM2TS, 0, path)
		else:
			ENIGMA_SERVICE_ID = 0
			DEFAULT_VIDEO_PID = 0x44
			DEFAULT_AUDIO_PID = 0x45
			service = eServiceReference(ENIGMA_SERVICE_ID, 0, path)
			service.setData(0, DEFAULT_VIDEO_PID)
			service.setData(1, DEFAULT_AUDIO_PID)
		service.setName(name)
		return service