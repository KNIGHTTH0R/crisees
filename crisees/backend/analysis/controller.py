#!/usr/bin/env python
# -*- coding: utf-8 -*-

from common import get_project_root
from db.crisees.models import BackendOrder
import os

'''
The analysis controller.
Responsible for obtaining a list of backend components and making them available to items that pass through.
Runs within the analysis thread.
'''
class Controller(object):
	
	def __init__(self, scanner):
		self.__scanner = scanner
		self.__run = []
		self.__imports = {}
	
	def parse(self, item):
		analysers = BackendOrder.objects.filter(source = self.__scanner.source, backend_module__pipe = 'ANALYSIS')
		
		# Based on the list of analysis components from the database model, loop through, attempt to hook up to the
		# component and pass an item to it to analyse.
		for each in analysers:
			if each not in self.__run:
				if each not in self.__imports.keys():
					if os.path.exists(os.path.join(get_project_root(), ('backend/analysis/pipe/%s.py' % each.backend_module.sys_name))):
						self.__imports[each] = __import__(('backend.analysis.pipe.%s' % each.backend_module.sys_name), fromlist = ['backend.analysis.pipe'])
					else:
						raise IOError
					
				item = self.__imports[each].parse(self.__scanner, item)
				
				self.__run.append(each)
			
		return item
	
	def reset(self):
		self.__run = []
