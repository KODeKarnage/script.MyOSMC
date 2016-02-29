

# XBMC Modules
import xbmc
import xbmcaddon
import xbmcgui

# STANDARD Modules
import sys
import os
import threading
import traceback

addonid 	= "script.module.OSMC_Walkthru"
__addon__   = xbmcaddon.Addon(addonid)
DIALOG      = xbmcgui.Dialog()
WINDOW 		= xbmcgui.Window(10000)
RESOURCES   = os.path.join(xbmcaddon.Addon(addonid).getAddonInfo('path'), 'resources','lib')
LIB_Folder	= os.path.join(RESOURCES, 'lib')
OSMCFolder 	= os.path.join(RESOURCES,' osmc')

sys.path.append(RESOURCES)

# Custom Modules
from OSMC_Common import osmc_logging, osmc_language, osmc_system
import osmc_walkthru

LOGGER    		= osmc_logging.StandardLogger(__addonid__)
LANGUAGER 		= osmc_language.LangRetriever(__addon__)

log  			= LOGGER.log
lang 			= LANGUAGER.lang


class OSMCSettingClass(object):

	''' 
		A OSMCSettingClass is way to substantiate the settings of an OSMC settings module, and make them available to the 
		OSMC Settings Addon (OSA).

	'''

	def __init__(self, modules = None):

		''' 
			The MASTER_SETTINGS contains all the settings in the settings group, as well as the methods to call when a
			setting_value has changed and the existing setting_value. 
		'''

		super(OSMCSettingClass, self).__init__()

		self.addonid = addonid
		self.me = xbmcaddon.Addon(self.addonid)

		# this is what is displayed in the main settings gui
		self.shortname 		= 'walkthru'
		self.FX_Icon 		= os.path.join(OSMCFolder, "FX_Icon.png")
		self.FO_Icon 		= os.path.join(OSMCFolder, "FO_Icon.png")
		self.FX_Icon_Widget = os.path.join(OSMCFolder, "FX_Icon_Widget.png")
		self.FO_Icon_Widget = os.path.join(OSMCFolder, "FO_Icon_Widget.png")


	def run(self, modules=None):

		vendor = check_vendor()

		log("Vendor is %s" % vendor)

		if modules is None:
			modules, _ = osmc_system.retrieve_modules()

		for module in modules:

			if module.addonid == "script.module.osmcsetting.networking":

				networking_instance = module

				self.open_gui(networking_instance)

				self.on_close()

				break


	def on_close(self):
		"""Actions to take after the walkthru closes
		"""

		with open('/tmp/walkthrough_completed', 'w+') as f:
			log('/tmp/walkthrough_completed written')

		osmc_system.move('/tmp/walkthrough_completed', '/walkthrough_completed')

		# Query user about whether they would like to update now
		update_check_now = False

		if vendor == 'noobs':

			update_check_now = DIALOG.yesno(lang(32026), lang(32027), lang(32028), lang(32029))

		elif vendor == 'ts':

			update_check_now = DIALOG.yesno(lang(32026), lang(32030), lang(32031), lang(32029))

		if update_check_now:
			self.call_for_update()


	def call_for_update(self):

		log('User elected to update now')

		try:

			address = '/var/tmp/osmc.settings.update.sockfile'

			message = ('settings_command', {'action': 'update'})

			message = json.dumps(message)

			sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
			sock.connect(address)
			sock.sendall(message) 
			sock.close()

		except Exception as e:

			log(traceback.format_exc())
			

	def open_gui(self, networking_instance, testing=False):

		xml = "walkthru.xml"

		lang_rerun 			= False
		first_run 			= True

		selected_language 	= None

		while first_run or lang_rerun:

			first_run = False
			
			GUI = osmc_walkthru.walkthru_gui(xml, scriptPath, 'Default', networking_instance=networking_instance, lang_rerun=lang_rerun, selected_language=selected_language, testing=testing)
			GUI.doModal()

			selected_language 	= GUI.selected_language
			skin_choice 		= GUI.selected_skin
			lang_rerun 			= GUI.lang_rerun

			# set language
			xbmc.executebuiltin('xbmc.SetGUILanguage(%s)' % selected_language)
			
			xbmc.sleep(1000)

			log('users language: %s' % selected_language)
			log('lang_rerun: %s' % lang_rerun)
			log('skin_choice: %s' % skin_choice)
			
		# -- THIS SECTION SHOULD BE SUPPRESSED WHILE THE SKIN CHANGE METHOD IS WORKED ON  --
		if skin_choice != 'OSMC':

			log('Loading Confluence')
			try:
				xbmc.setskin('skin.confluence')
			except:
				log('Loading Confluence failed.')

		log('Exiting GUI')



if __name__ == "__main__":
	pass

