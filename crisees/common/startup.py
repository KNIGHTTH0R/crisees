#!/usr/bin/env python
# -*- coding: utf-8 -*-

from terminal import statuses, welcomes
import urllib2

required_packages = [
	'whoosh',
	'anyjson',
	'django',
	'pytz',
	'gdata',
	'httplib2',
	'os',
	'simplejson',
	'urllib2',
	'datetime',
	'operator',
	're',]

def check_packages():
	for package in required_packages:
		try:
			__import__(package)
			print statuses.success("Package '%s' found." % package)
		except ImportError:
			print statuses.fail(
				("Couldn't find the required package '%s'." % package),
				("Please check that the '%s' package is correctly installed." % package))
			quit()

def check_connection():
	try:
		urllib2.urlopen('http://google.com', timeout = 1)
		print statuses.success("Internet connection active.")
	except urllib2.URLError:
		print statuses.fail(
			"Couldn't test your connection to the Internet.",
			"Please check your Internet connectivity, and try again.")
		quit()
	

welcomes.startup()
check_packages()
#check_connection()
