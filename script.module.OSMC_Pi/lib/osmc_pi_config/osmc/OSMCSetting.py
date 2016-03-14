

# XBMC Modules
import xbmc
import xbmcaddon
import xbmcgui

# STANDARD Modules
import subprocess
import sys
import os
import threading
import traceback

addonid 	= "script.module.OSMC_Pi"
__addon__   = xbmcaddon.Addon(addonid)
DIALOG      = xbmcgui.Dialog()
RESOURCES   = os.path.join(xbmcaddon.Addon(addonid).getAddonInfo('path'), 'resources','lib')
LIB_Folder	= os.path.join(RESOURCES, 'lib')
OSMCFolder 	= os.path.join(RESOURCES,' osmc')

# Custom modules
sys.path.append(RESOURCES)

# OSMC SETTING Modules
import OSMC_REparser as parser
from OSMC_Common import osmc_logging, osmc_language, osmc_system

LOGGER    		= osmc_logging.StandardLogger(__addonid__)
LANGUAGER 		= osmc_language.LangRetriever(__addon__)

log  			= LOGGER.log
lang 			= LANGUAGER.lang


class OSMCSettingClass(object):

	''' 
		A OSMCSettingClass is way to substantiate the settings of an OSMC settings module, and make them available to the 
		OSMC Settings Addon (OSA).

	'''

	def __init__(self):

		''' 
			The MASTER_SETTINGS contains all the settings in the settings group, as well as the methods to call when a
			setting_value has changed and the existing setting_value. 
		'''

		super(OSMCSettingClass, self).__init__()

		self.addonid = addonid
		self.me = xbmcaddon.Addon(self.addonid)

		# this is what is displayed in the main settings gui
		self.shortname = 'Pi Config'
		self.FX_Icon 		= os.path.join(OSMCFolder, "FX_Icon.png")
		self.FO_Icon 		= os.path.join(OSMCFolder, "FO_Icon.png")
		self.FX_Icon_Widget = os.path.join(OSMCFolder, "FX_Icon_Widget.png")
		self.FO_Icon_Widget = os.path.join(OSMCFolder, "FO_Icon_Widget.png")

		# the location of the config file FOR TESTING ONLY
		try:								
			self.config_location = '/boot/config.txt'

			self.populate_misc_info()

		except:

			# if anything fails above, assume we are testing and look for the config
			# in the testing location
			self.config_location = '/home/plaskev/Documents/config.txt'

		try:
			self.clean_user_config()
		except Exception:

			log('Error cleaning users config')
			log(traceback.format_exc())


	def run(self):

		'''
			The method determines what happens when the item is clicked in the settings GUI.
			Usually this would be __addon__.OpenSettings(), but it could be any other script.
			This allows the creation of action buttons in the GUI, as well as allowing developers to script and skin their 
			own user interfaces.
		'''

		# read the config.txt file everytime the settings are opened. This is unavoidable because it is possible for
		# the user to have made manual changes to the config.txt while OSG is active.
		config = parser.read_config_file(self.config_location)

		extracted_settings = parser.config_to_kodi(parser.MASTER_SETTINGS, config)

		# load the settings into kodi
		log('Settings extracted from the config.txt')
		for k, v in extracted_settings.iteritems():

			log("%s : %s" % (k, v))
			self.me.setSetting(k, str(v))

		# open the settings GUI and let the user monkey about with the controls
		self.me.openSettings()

		# retrieve the new settings from kodi 
		new_settings = self.settings_retriever_xml()

		log('New settings applied to the config.txt')
		for k, v in new_settings.iteritems():
			log("%s : %s" % (k, v))

		# read the config into a list of lines again
		config = parser.read_config_file(self.config_location)

		# construct the new set of config lines using the protocols and the new settings
		new_settings = parser.kodi_to_config(parser.MASTER_SETTINGS, config, new_settings)

		# write the new lines to the temporary config file
		parser.write_config_file('/var/tmp/config.txt', new_settings)

		# copy over the temp config.txt to /boot/ as superuser
		subprocess.call(["sudo", "mv",  '/var/tmp/config.txt', self.config_location])

		ok = DIALOG.notification(lang(32095), lang(32096))


	def apply_settings(self):

		pass 


	def settings_retriever_xml(self):

		''' 
			Reads the stored settings (in settings.xml) and returns a dictionary with the setting_name: setting_value. This 
			method cannot be overwritten.
		'''

		latest_settings = {}

		addon = xbmcaddon.Addon(self.addonid)

		for key in parser.MASTER_SETTINGS.keys():

			latest_settings[key] = addon.getSetting(key)

		return latest_settings


	def populate_misc_info(self):

		# grab the Pi serial number and check to see whether the codec licences are enabled
		mpg = subprocess.check_output(["/opt/vc/bin/vcgencmd", "codec_enabled", "MPG2"])
		wvc = subprocess.check_output(["/opt/vc/bin/vcgencmd", "codec_enabled", "WVC1"])
		serial_raw = subprocess.check_output(["cat", "/proc/cpuinfo"])

		# grab just the serial number
		serial = serial_raw[serial_raw.index('Serial') + len('Serial'):].replace('\n','').replace(':','').replace(' ','').replace('\t','')

		# load the values into the settings gui
		__addon__.setSetting('codec_check', mpg.replace('\n','') + ', ' + wvc.replace('\n',''))
		__addon__.setSetting('serial', serial)


	def clean_user_config(self):
		''' Comment out problematic lines in the users config.txt '''

		patterns = [

			r".*=.*\[remove\].*", 
			r".*=remove",
		]

		config = parser.read_config_file(self.config_location)

		new_config = parser.clean_config(config, patterns)

		# write the new lines to the temporary config file
		parser.write_config_file('/var/tmp/config.txt', new_config)

		# copy over the temp config.txt to /boot/ as superuser
		subprocess.call(["sudo", "mv",  '/var/tmp/config.txt', self.config_location])


if __name__ == "__main__":
	pass

