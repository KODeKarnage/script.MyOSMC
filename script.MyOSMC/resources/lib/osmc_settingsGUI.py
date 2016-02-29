# XBMC modules
import xbmc
import xbmcaddon
import xbmcgui

# STANDARD library modules
import imp
import os
import sys
import traceback

path       = xbmcaddon.Addon().getAddonInfo('path')
lib        = os.path.join(path, 'resources','lib')
media      = os.path.join(path, 'resources','skins','Default','media')

sys.path.append(xbmc.translatePath(lib))

__addon__  = xbmcaddon.Addon()
scriptPath = __addon__.getAddonInfo('path')
WINDOW     = xbmcgui.Window(10000)

# Custom modules
sys.path.append(xbmc.translatePath(os.path.join(xbmcaddon.Addon().getAddonInfo('path'), 'resources','lib')))
from OSMC_Common import osmc_logging, osmc_language, osmc_system


__addon__       = xbmcaddon.Addon()
__addonid__     = __addon__.getAddonInfo('id')
__setting__     = __addon__.getSetting
DIALOG          = xbmcgui.Dialog()

LOGGER    		= osmc_logging.StandardLogger(__addonid__)
LANGUAGER 		= osmc_language.LangRetriever(__addon__)

log  			= LOGGER.log
lang 			= LANGUAGER.lang


class OSMC_gui(xbmcgui.WindowXMLDialog):

	def __init__(self, strXMLname, strFallbackPath, strDefaultName, **kwargs):

		self.live_modules   = kwargs.get('live_modules' , [])

		self.module_holder = {}


	def onInit(self):

		# add the exit button
		self.getControl(555).addItem(xbmcgui.ListItem(label='Exit', label2=''))

		# place the items into the gui
		for i, module in enumerate(self.live_modules):

			# set the icon (texturefocus, texturenofocus)
			list_item = xbmcgui.ListItem(label=module.shortname, label2='', thumbnailImage = module.FX_Icon)
			list_item.setProperty('FO_ICON', module.FO_Icon)

			controlID = 555

			self.module_holder[i + 1] = module

			self.getControl(controlID).addItem(list_item)

		# add in the Update Now button if the notification is 'true'
		if xbmcgui.Window(10000).getProperty('OSMC_notification') == 'true':
			self.getControl(555).addItem(xbmcgui.ListItem(label=lang(32038)))

		# add text to changelog box
		# this is temporary text while Naz works on making the changelog available.
		tmp = "this is temporary text purely for testing, if you are seeing this in the live version of OSMC then someone done screwed up"
		self.getControl(2222).setText(tmp)
		self.setFocusId(555)


	def onAction(self, action):

		actionID = action.getId()
		focused_control = self.getFocusId()

		if (actionID in (10, 92)):
			self.close()


	def onClick(self, controlID):

		if controlID == 909:
			# open the advanced settings beta addon
			xbmc.executebuiltin("RunAddon(script.advancedsettingsetter)")

		else:

			pos = self.getControl(555).getSelectedPosition()

			if pos == 0:
				self.close()

			elif pos not in range(len(self.module_holder) + 1 ):
				# the Update Now button is added to the List but not included in the module_holder dict
				# so if we get a button press that is not in the range defined by the length of the module list plus 
				# 1 to account for the zero indexing, then we can correctly presume it is this last button.
				# To be clear, there is no way any pos can be sent that wont be in the normal list.

				xbmc.executebuiltin('RunScript(/usr/share/kodi/addons/script.module.osmcsetting.updates/resources/lib/call_parent.py, update)')

			else:

				instance = self.module_holder.get(pos, None)

				if instance is not None:
					
					instance.run()


	def onFocus(self, controlID):

		pass

