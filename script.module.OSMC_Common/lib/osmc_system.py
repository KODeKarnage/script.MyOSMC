"""
Module to house functions relating to the system in general.

i.e. to identify hardware OSMC is installed on, whether it is a n00bs install, etc.


"""

import imp
import os
import subprocess
import traceback
import xbmc

def check_vendor():
	''' Checks whether OSMC is being installed via N00bs or ts.
		Returns None if the vendor file is not present or does not contain 'noobs' or 'ts'.
		Vendor is pass to the Main settings service, which then asks the user whether they would like 
		to update (noobs or ts only).
	'''

	if os.path.isfile('/vendor'):
		with open('/vendor', 'r') as f:
			line = f.readline()

		if 'noobs' in line:
			return 'noobs'

		if 'ts' in line:
			return 'ts'

	return None


def get_version():

	''' Loads the current OSMC version into the Home window for display in MyOSMC '''

	# Check for "upgraded" Alpha 4 and earlier

	fnull = open(os.devnull, 'w')

	process = subprocess.call(['/usr/bin/dpkg-query', '-l', 'rbp-mediacenter-osmc'], stderr=fnull, stdout=fnull)

	fnull.close()

	if process == 0:

		version_string = 'Unsupported OSMC Alpha release'

	else:

		version = []
	
		with open('/etc/os-release','r') as f:

			tags = ['NAME=', 'VERSION=', 'VERSION_ID=']

			lines = f.readlines()

			for line in lines:

				for tag in tags:

					if line.startswith(tag):
						version.append(line[len(tag):].replace('"','').replace('\n',''))

		version_string = ' '.join(version)

	return version_string


def retrieve_modules(known_modules_order=None, exclude=[]):
	'''
		Scans for MyOSMC modules, returns an ordered list of the instances of each setting module class, and
		a list of the modules that failed to import along with their tracebacks.

		The failed list contains tuples of the folder name, the path and the traceback.

		The scan is done on the usr/share folder first, and the users own addon folder second.
		The addon folder versions of the module will overwrite the usr/share version.

		known_modules_order is an optional dictionary containing the order of known modules. The key is the folder name
		(i.e. "script.module.osmcsetting.pi") and the value is an integer indicating the desired order.

		exclude is an optional list of known module to exclude from the search. (Most commonly the walkthru, which should not be displayed)

	'''

	MyOSMC_Modules = []
	failed = []

	addon_paths = [
		'/usr/share/kodi/addons',
		os.path.join(xbmc.translatePath("special://home"), "addons/")
	]

	for addon_path in addon_paths:

		# retrieve the folders in the path
		folders  = os.listdir(addon_path)

		for folder in folders:

			if folder in exclude:
				continue

			try:
				setting_instance = inspect_folder(addon_path, folder)

			except:
				failed.append((folder, addon_path, traceback.format_exc()))
				continue
			
			MyOSMC_Modules.append((folder, setting_instance))

	# remove the blank entries
	MyOSMC_Modules = [x for x in MyOSMC_Modules if x[1] is not None]

	print '3'
	print MyOSMC_Modules

	# sort alphabetically, then sort by the known_modules_order placing the unknown modules at the end (still in alphabetical order)
	sorted(MyOSMC_Modules, key= lambda x: x[0])

	if known_modules_order is not None:
		sorted(MyOSMC_Modules, key= lambda x: known_modules_order.get(x[0], 999))

	return [x[1] for x in MyOSMC_Modules], failed


def inspect_folder(addon_folder, sub_folder):
	'''
		Checks the provided folder to see if it is a genuine OSMC module.
	'''

	# check for OSMCSetting.py, return None is it doesnt exist
	osmc_setting_file = os.path.join(addon_folder, sub_folder, "resources", "osmc", "OSMCSetting.py")

	if not os.path.isfile(osmc_setting_file): 
		raise

	# import the OSMCSetting.py file
	OSMCSetting = imp.load_source(sub_folder.replace('.',''), osmc_setting_file)

	return OSMCSetting.OSMCSettingClass


def walkthrough_completed():
	"""Returns a boolen of True if the walkthru has been completed, otherwise False"""

	return os.path.isfile('/walkthrough_completed')


def get_timezones():

	''' Returns a dictionary or regions, which hold lists of countries within those regions. '''

	with open('/usr/share/zoneinfo/zone.tab', 'r') as f:

		lines = f.readlines()

		lines = [line for line in lines if line and not line.startswith('#') and '/' in line]

	tmp = []
	timezones = {'UTC': ['UTC']}

	for line in lines:

		columns = line.split('\t')

		try:
			tz_raw = columns[2].replace('\n','')
		except:
			continue

		tmp.append(tz_raw)

	tmp.sort()

	for tz_raw in tmp:

		tz_region, tz_country = tz_raw[:tz_raw.index('/')], tz_raw[tz_raw.index('/')+1:]

		t = timezones.get(tz_region, [])

		t.append(tz_country)

		timezones[tz_region] = t

	return timezones


def get_languages():
	
	# try and find language files (Kodi 14.x)
	try:
		return [folder for folder in os.listdir('/usr/share/kodi/language/')]
	except:
		pass
	# if we have not found yet try looking for laonguage addons (Kodi 15.x)
	languages = ['English']
	languagedirs = ["/home/osmc/.kodi/addons", "/usr/share/kodi/addons" ]
	language_folder_contents = []

	try:
		language_folder_contents = os.listdir(languagedirs[0])
	except:
		pass
	
	try:
		language_folder_contents = os.listdir(languagedirs[1])
	except:
		pass

	for folder in language_folder_contents:
		if folder.startswith('resource.language.'):
			try:
				tree = ET.parse('/home/osmc/.kodi/addons/' + folder + os.sep + 'addon.xml')
			except:
				tree = ET.parse('/usr/share/kodi/addons/' + folder + os.sep + 'addon.xml')
			root = tree.getroot()
			languages.append(root.attrib['name'])

	return languages


def move(from_, to_):

	subprocess.call(['sudo', 'mv', from_, to_])


def delete(this_):

	subprocess.call(['sudo', 'rm', this_])


def is_Vero(self):
	'''
		Checks whether this is a Vero and whether the warranty info should be shown 
	'''

	# generate the URL
	with open('/proc/cmdline', 'r') as f:

		line = f.readline()

		settings = line.split(' ')

		for setting in settings:

			if setting.startswith('osmcdev='):

				if 'vero' in setting or 'vero2' in setting:

					return True

	return False

