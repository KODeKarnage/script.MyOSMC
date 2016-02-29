import sys
import threading

import xbmc, xbmcaddon

sys.path.append(xbmc.translatePath(os.path.join(xbmcaddon.Addon().getAddonInfo('path'), 'resources','lib')))

# Custom Modules
from OSMC_Common import osmc_logging, osmc_language, osmc_system

__addon__  	= xbmcaddon.Addon()
scriptPath 	= __addon__.getAddonInfo('path')

LOGGER    	= osmc_logging.StandardLogger(__addonid__)
LANGUAGER 	= osmc_language.LangRetriever(__addon__)

log  		= LOGGER.log
lang 		= LANGUAGER.lang


class mock_Networking_caller(object):

	def __init__(self, parent, net_call):

		self.ftr_running = False
		self.timeout     = 0
		self.parent = parent
		self.parent.internet_connected = True

	def start(self):

		pass

	def setDaemon(self, bool):

		pass


class Networking_caller(threading.Thread):

	def __init__(self, parent, net_call):

		super(Networking_caller, self).__init__()

		self.daemon      = True
		self.cancelled   = False
		self.parent      = parent
		self.net_call    = net_call
		self.ftr_running = True
		self.timeout     = 0


	def run(self):
		"""Calls Barkers method to check for network connection"""

		log('checking internet connection')

		while self.ftr_running and self.timeout < 12:

			self.ftr_running = self.net_call.is_ftr_running()

			# break early if ftr is not running
			if not self.ftr_running: break

			self.timeout += 1

			xbmc.sleep(10000)

		if not self.ftr_running:

			self.parent.internet_connected = self.net_call.check_network(False)

		else:
			# ftr_running has timed out, consider it ended and leave internet_connected as False
			self.ftr_running = False

		log('network connection is %s' % self.parent.internet_connected)
		log('internet connection is %s' % self.net_call.check_network(True))
