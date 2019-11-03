#!/usr/bin/env python
# -*- coding: utf-8 -*-

from common import get_project_root
from db.crisees.models import BackendOrder
import os

class Controller(object):
	
	def __init__(self, scanner):
		self.__scanner = scanner
		self.__run = []
		self.__imports = {}
	
	def parse(self, item):
		filters = BackendOrder.objects.filter(source = self.__scanner.source, backend_module__pipe = 'FILTER').order_by('step')
		
		for each in filters:
			if each not in self.__run:
				if each not in self.__imports.keys():
					if os.path.exists(os.path.join(get_project_root(), ('backend/filtering/pipe/%s.py' % each.backend_module.sys_name))):
						self.__imports[each] = __import__(('backend.filtering.pipe.%s' % each.backend_module.sys_name), fromlist = ['backend.filtering.pipe'])
					else:
						raise IOError
				
				item = self.__imports[each].parse(self.__scanner, item)
				
				if item is None:
					break
				
				self.__run.append(each)
		
		return item
	
	def reset(self):
		self.__run = []
