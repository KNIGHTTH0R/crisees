#!/usr/bin/env python
# -*- coding: utf-8 -*-

from backend.managers.analysis import Analysis
from backend.managers.sourcing import Sourcing

class Controller(object):
	
	def __init__(self):
		self.analysis = Analysis()
		self.sourcing = Sourcing(self.analysis)
	
	def stop(self):
		self.sourcing.stop()
		self.analysis.stop()
	
	def start(self):
		print
		print "Analysis components initialised; ready for action!"
		print "Any sources that are activated will now be started.\n"
		
		self.analysis.start()
		self.sourcing.start()
