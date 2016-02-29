import os
import sys
import xbmc, xbmcaddon

sys.path.append(xbmc.translatePath(os.path.join(xbmcaddon.Addon('script.module.OSMC_Common').getAddonInfo('path'), 'resources','lib')))
import osmc_system


if len(sys.argv) > 1:

	target = sys.argv[1]

	modules, _ = osmc_system.retrieve_modules()

	for instance in modules:

		if instance.addonid == target:

			instance.run()
			break

	
