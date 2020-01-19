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
import shutil


def readFile(path):
	try:
		f = open(path, "r")
		data = f.read()
		f.close()
		return data
	except Exception as e:
		print("MVC-I: FileUtils: readFile: path: %s, exception: %s" % (path, e))
		return ""


def writeFile(path, data):
	try:
		f = open(path, "w")
		f.write(data)
		f.close()
	except Exception as e:
		print("MVC-E: FileUtils: writeFile: path: %s, exception: %s" % (path, e))


def deleteFile(path):
	try:
		os.remove(path)
	except Exception as e:
		print("MVC-E: FileUtils: deleteFile: exception: path: %s, exception: %s" % (path, e))


def copyFile(src_path, dest_path):
	try:
		shutil.copyfile(src_path, dest_path)
	except Exception as e:
		print("MVC-E: FileUtils: copyFile: exception: src_path: %s, dest_path: %s, exception: %s" % (src_path, dest_path, e))


def createDirectory(path):
	return os.popen("mkdir -p %s" % path).read()


def deleteDirectory(path):
	try:
		shutil.rmtree(path)
	except Exception as e:
		print("MVC-E: FileUtils: deleteDirectory: exception: path: %s, exception: %s" % (path, e))
