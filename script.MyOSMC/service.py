#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
 Copyright (C) 2016 KodeKarnage

 This Program is free software; you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation; either version 2, or (at your option)
 any later version.

 This Program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with XBMC; see the file COPYING.  If not, write to
 the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
 http://www.gnu.org/copyleft/gpl.html
'''

import os
import sys
import xbmc
import xbmcaddon
import xbmcgui

__addon__  = xbmcaddon.Addon()
scriptPath = __addon__.getAddonInfo('path')
WINDOW     = xbmcgui.Window(10000)

# Custom modules
sys.path.append(xbmc.translatePath(os.path.join(xbmcaddon.Addon().getAddonInfo('path'), 'resources','lib')))
import osmc_settingsGUI
from OSMC_Common import osmc_logging, osmc_system


if __name__ == "__main__":

	# on start up, make the modules available to the widget
	known_modules_order = 	{
								"script.module.osmcsetting.updates":				0,
								"script.module.osmcsetting.networking":				1,
								"script.module.osmcsetting.pi":						2,
								"script.module.osmcsetting.pioverclock":			3,
								"script.module.osmcsetting.logging":				4, 
								"script.module.osmcsetting.apfstore":				5,
								"script.module.osmcsetting.services":				6,
								"script.module.osmcsetting.remotes":				7,

								}

	modules = osmc_system.retrieve_modules(known_modules_order)

	script_location = os.path.join(scriptPath, 'resources', 'lib', 'open_osmc_module.py')
	
	WINDOW.setProperty('MyOSMC.Module.Script', script_location)

	offset = 0

	for i, instance in enumerate(modules):

		if instance.shortname == 'walkthru':
			offset -= 1
			# check for walkthrough completed, if not found, then run the walkthru
			if not osmc_system.walkthrough_completed():
				instance.run(modules)

			continue

		WINDOW.setProperty('MyOSMC.Module.%s.name' 		% i - offset, instance.shortname)
		WINDOW.setProperty('MyOSMC.Module.%s.fo_icon' 	% i - offset, instance.FO_Icon_Widget)
		WINDOW.setProperty('MyOSMC.Module.%s.fx_icon' 	% i - offset, instance.FX_Icon_Widget)
		WINDOW.setProperty('MyOSMC.Module.%s.id' 		% i - offset, instance.addonid)

