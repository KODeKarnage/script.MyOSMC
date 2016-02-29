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

# Custom modules
sys.path.append(xbmc.translatePath(os.path.join(xbmcaddon.Addon().getAddonInfo('path'), 'resources','lib')))
from OSMC_Common import osmc_logging, osmc_language, osmc_system
import osmc_settingsGUI

__addon__       = xbmcaddon.Addon()
__addonid__     = __addon__.getAddonInfo('id')

LOGGER    		= osmc_logging.StandardLogger(__addonid__)
LANGUAGER 		= osmc_language.LangRetriever(__addon__)

log  			= LOGGER.log
lang 			= LANGUAGER.lang


if __name__ == "__main__":

	log('MyOSMC starting')

	version = osmc_system.get_version()

	log('Current Version: %s' % version_string)

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

	exclude = ['script.module.MyOSMC.walkthru',]

	modules, failed = osmc_system.retrieve_modules(known_modules_order, exclude)

	for failure in failed:
		log("Failed to import %s from %s\n%s", failure)							

	# window xml to use
	xml = "settings_gui.xml"

	# instantiate the window
	GUI = osmc_settingsGUI.OSMC_gui(xml, scriptPath, 'Default', live_modules=modules)

	GUI.doModal()

	log('Exiting OSMC Settings')
