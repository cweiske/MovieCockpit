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
from __init__ import _
from Version import VERSION
from Components.config import config
from Plugins.Plugin import PluginDescriptor
from Screens.InfoBar import InfoBar
from Tools.BoundFunction import boundFunction
from FileCache import FileCache
from ConfigInit import ConfigInit
from RecordingControl import RecordingControl
from SkinUtils import initPluginSkinPath, loadPluginSkin
from Trashcan import Trashcan
from ConfigScreen import ConfigScreen
from Debug import createLogFile
from StylesOps import applyPluginStyle


def openSettings(session, **__):
	print("MVC-I: plugin: openSettings")
	session.open(ConfigScreen)


def openMovieSelection(session, **__):
	print("MVC-I: plugin: openMovieSelection")
	from MovieSelection import MovieSelection
	session.openWithCallback(reloadMovieSelection, MovieSelection)


def reloadMovieSelection(session=None, reload_movie_selection=False):
	if reload_movie_selection:
		print("MVC-I: plugin: reloadMovieSelection")
		openMovieSelection(session)


def autostart(reason, **kwargs):
	if reason == 0:  # startup
		if "session" in kwargs:
			if config.plugins.moviecockpit.debug.value:
				createLogFile()
			print("MVC-I: plugin: +++ Version: " + VERSION + " starts...")
			print("MVC-I: plugin: autostart: reason: %s" % reason)
			session = kwargs["session"]
			if not config.plugins.moviecockpit.disable.value:
				launch_key = config.plugins.moviecockpit.launch_key.value
				if launch_key == "showMovies":
					InfoBar.showMovies = boundFunction(openMovieSelection, session)
				elif launch_key == "showTv":
					InfoBar.showTv = boundFunction(openMovieSelection, session)
				elif launch_key == "showRadio":
					InfoBar.showRadio = boundFunction(openMovieSelection, session)
				elif launch_key == "openQuickbutton":
					InfoBar.openQuickbutton = boundFunction(openMovieSelection, session)
				elif launch_key == "startTimeshift":
					InfoBar.startTimeshift = boundFunction(openMovieSelection, session)
			ConfigScreen.setEPGLanguage()
			RecordingControl()
			FileCache.getInstance()
			Trashcan.getInstance()
			initPluginSkinPath()
			applyPluginStyle()
			loadPluginSkin("skin.xml")
	elif reason == 1:  # shutdown
		print("MVC-I: plugin: --- shutdown")
		if not os.path.exists("/etc/enigma2/.moviecockpit"):
			FileCache.getInstance().closeDatabase()
	else:
		print("MVC-I: plugin: autostart: reason not handled: %s" % reason)


def Plugins(**__):
	print("MVC-I: plugin: +++ Plugins")
	ConfigInit()
	descriptors = []
	descriptors.append(
		PluginDescriptor(
			where=[
				PluginDescriptor.WHERE_SESSIONSTART,
				PluginDescriptor.WHERE_AUTOSTART
			],
			fnc=autostart))

	if config.plugins.moviecockpit.extmenu_settings.value:
		descriptors.append(
			PluginDescriptor(
				name="MovieCockpit" + " - " + _("Setup"),
				description=_("Open setup"),
				icon="MovieCockpit.svg",
				where=[
					PluginDescriptor.WHERE_PLUGINMENU,
					PluginDescriptor.WHERE_EXTENSIONSMENU
				],
				fnc=openSettings
			)
		)

	if config.plugins.moviecockpit.extmenu_plugin.value and not config.plugins.moviecockpit.disable.value:
		descriptors.append(
			PluginDescriptor(
				name="MovieCockpit",
				description=_("Manage recordings"),
				icon="MovieCockpit.svg",
				where=[
					PluginDescriptor.WHERE_PLUGINMENU,
					PluginDescriptor.WHERE_EXTENSIONSMENU
				],
				fnc=openMovieSelection
			)
		)
	return descriptors
