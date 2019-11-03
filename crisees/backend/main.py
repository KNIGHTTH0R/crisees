#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.core.management import setup_environ
from backend.managers.controller import Controller
from backend import settings
from common.terminal import welcomes, highlight, statuses, Colours

'''
Imports all the settings from the Django settings.py file.
'''
def import_settings():
	setup_environ(settings)
	print statuses.success("Crisees settings successfully imported.")

'''
Kills the controller, so the process can die.
'''
def stop(controller):
	print highlight("\nShutting down backend...", colour = Colours.Yellow, bold = True)
	print highlight("Please give this some time, as several threads need to be wound down.\n", colour = Colours.Yellow)
	controller.stop()

'''
Greets the user, and starts the controller.
Hooks the KeyboardInterrupt (CTRL+C) to kill off the controller.
'''
def start():
	import_settings()
	welcomes.backend()
	
	controller = None
	
	try:
		controller = Controller()
		controller.start()
	except KeyboardInterrupt:
		print
		stop(controller)
