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
from MovieCover import MovieCover
from MovieTMDB import MovieTMDB
from Tasker import Tasker
from MountPoints import getMountPoint, getDiskSpaceInfo
from FileCache import FileCache, FILE_TYPE_FILE, FILE_TYPE_DIR


FILE_OP_DELETE = 1
FILE_OP_MOVE = 2
FILE_OP_COPY = 3


class FileOps(MovieTMDB, MovieCover, Tasker):

	def __init__(self):
		MovieTMDB.__init__(self)
		MovieCover.__init__(self)
		Tasker.__init__(self)
		self.execution_list = []

	def reloadList(self, path):
		print("MVC-E: FileOps: reloadList: path: %s" % path)
		print("MVC-E: FileOps: reloadList: should not be called at all, as overridden by child")

	def execFileOpsNoProgress(self, execution_list):
		print("MVC-I: FileOps: execFileOpsNoProgress: execution_list: " + str(execution_list))
		self.execution_list = execution_list
		if self.execution_list:
			self.execNextFileOp()

	def execNextFileOp(self):
		op, path, target_path, filetype = self.execution_list.pop(0)
		print("MVC-I: FileOps: execNextFileOp: op: %s, path: %s, target_path: %s, filetype: %s" % (op, path, target_path, filetype))
		if path and not path.endswith(".."):
			self.execFileOp(op, path, target_path, filetype)
		else:
			if self.execution_list:
				self.execNextFileOp()

	def execFileOpCallback(self, op, path, target_path, filetype):
		print("MVC-I: FileOps: execFileOpCallback: op: %s, path: %s, target_path: %s, filetype: %s" % (op, path, target_path, filetype))
		self.reloadList(os.path.dirname(path))
		if self.execution_list:
			self.execNextFileOp()

	def execFileOp(self, op, path, target_path, filetype):
		cmd = []
		association = []
		print("MVC-I: FileOps: execFileOp: op: %s, path: %s, target_path: %s, filetype: %s" % (op, path, target_path, filetype))
		if op == FILE_OP_DELETE:
			c = self.__execFileDelete(path, filetype)
			cmd.append(c)
			association.append((self.__deleteCallback, path, target_path, filetype))
		elif op == FILE_OP_MOVE:
			if os.path.dirname(path) != target_path:
				free = 0
				used = 0
				if filetype != FILE_TYPE_FILE:
					_count, used = FileCache.getInstance().getCountSize(path)
					_used_percent, _used, free = getDiskSpaceInfo(target_path)
					#print("MVC: FileOps: execFileOp: move_dir: used: %s, free: %s" % (used, free))
				if free >= used:
					c = self.__execFileMove(path, target_path, filetype)
					cmd.append(c)
					association.append((self.__moveCallback, path, target_path, filetype))
				else:
					print("MVC-I: FileOps: execFileOp: move_dir: not enough space left: size: %s, free: %s" % (used, free))
			else:
				c = [":"]  # noop
				cmd.append(c)
		elif op == FILE_OP_COPY:
			if os.path.dirname(path) != target_path:
				c = self.__execFileCopy(path, target_path, filetype)
				cmd.append(c)
				association.append((self.__copyCallback, path, target_path, filetype))
			else:
				c = [":"]  # noop
				cmd.append(c)
		if cmd:
			#print("MVC: FileOps: execFileOp: cmd: %s" % cmd)
			association.append((self.execFileOpCallback, op, path, target_path, filetype))
			# Sync = True: Run script for one file do association and continue with next file
			self.shellExecute(cmd, association, True)

	def __deleteCallback(self, path, target_path, filetype):
		print("MVC-I: MovieSelection: __deleteCallback: path: %s, target_path: %s, filetype: %s" % (path, target_path, filetype))
		FileCache.getInstance().delete(path, filetype)

	def __moveCallback(self, path, target_path, filetype):
		print("MVC-I: FileOps: __moveCallback: path: %s, target_path: %s, filetype: %s" % (path, target_path, filetype))
		FileCache.getInstance().move(path, target_path, filetype)

	def __copyCallback(self, path, target_path, filetype):
		print("MVC-I: FileOps: __copyCallback: path: %s, target_path: %s, filetype: %s" % (path, target_path, filetype))
		FileCache.getInstance().copy(path, target_path, filetype)

	def __execFileDelete(self, path, filetype):
		print("MVC-I: FileOps: __execFileDelete: path: %s, filetype: %s" % (path, filetype))
		c = []
		if filetype == FILE_TYPE_FILE:
			cover_path, backdrop_path = self.getCoverPath(path)
			c.append('rm -f "' + cover_path + '"')
			c.append('rm -f "' + backdrop_path + '"')
			c.append('rm -f "' + self.getInfoPath(path) + '"')
			path, _ext = os.path.splitext(path)
			c.append('rm -f "' + path + '."*')
		elif filetype == FILE_TYPE_DIR:
			c.append('rm -rf "' + path + '"')
		#print("MVC: FileOps: __execFileDelete: c: %s" % c)
		return c

	def __execFileMove(self, path, target_path, filetype):
		print("MVC-I: FileOps: __execFileMove: path: %s, target_path: %s, filetype: %s" % (path, target_path, filetype))
		c = self.__changeFileOwner(path, target_path)
		if filetype == FILE_TYPE_FILE:
			cover_path, backdrop_path = self.getCoverPath(path)
			cover_target_path, _backdrop_target_path = self.getCoverPath(target_path)
			info_path = self.getInfoPath(path)
			info_target_path = self.getInfoPath(target_path)
			cover_target_dir = os.path.splitext(cover_target_path)[0] + "/"
			backdrop_target_dir = os.path.splitext(cover_target_path)[0] + "/"
			info_target_dir = os.path.splitext(info_target_path)[0] + "/"

			#print("MVC: File_Ops: __execFileMove: cover_path: %s, cover_target_dir: %s" % (cover_path, cover_target_dir))
			#print("MVC: File_Ops: __execFileMove: backdrop_path: %s, backdrop_target_dir: %s" % (backdrop_path, backdrop_target_dir))
			#print("MVC: File_Ops: __execFileMove: inof_path: %s, info_target_dir: %s" % (info_path, info_target_dir))

			c.append('mv "' + cover_path + '" "' + cover_target_dir + '"')
			c.append('mv "' + backdrop_path + '" "' + backdrop_target_dir + '"')
			c.append('mv "' + info_path + '" "' + info_target_dir + '"')

			path, _ext = os.path.splitext(path)
			if os.path.basename(target_path) == "trashcan":
				c.append('touch "' + path + '."*')
			c.append('mv "' + path + '."* "' + target_path + '/"')
		elif filetype == FILE_TYPE_DIR:
			if os.path.basename(target_path) == "trashcan":
				c.append('touch "' + path + '"')
			c.append('mv "' + path + '" "' + target_path + '"')
		#print("MVC: FileOps: __execFileMove: c: %s" % c)
		return c

	def __execFileCopy(self, path, target_path, filetype):
		print("MVC-I: FileOps: __execFileCopy: path: %s, target_path: %s, filetype: %s" % (path, target_path, filetype))
		c = self.__changeFileOwner(path, target_path)
		if filetype == FILE_TYPE_FILE:
			path, _ext = os.path.splitext(path)
			c.append('cp "' + path + '."* "' + target_path + '/"')
		elif filetype == FILE_TYPE_DIR:
			c.append('cp -ar "' + path + '" "' + target_path + '"')
		#print("MVC: FileOps: __execFileCopy: c: %s" % c)
		return c

	def __changeFileOwner(self, path, target_path):
		c = []
		if getMountPoint(target_path) != getMountPoint(path):
			# need to change file ownership to match target filesystem file creation
			tfile = "\"" + target_path + "/owner_test" + "\""
			path = path.replace("'", "\'")
			sfile = "\"" + path + ".\"*"
			c.append("touch %s;ls -l %s | while read flags i owner group crap;do chown $owner:$group %s;done;rm %s" % (tfile, tfile, sfile, tfile))
		return c
