#!/usr/bin/env python
# -*- coding: utf-8 -*-

from time import sleep
from common import list_difference
import threading

class Scanner(threading.Thread):
	
	def __init__(self, source, analysis_manager):
		super(Scanner, self).__init__()
		self.source = source
		self.analysis_manager = analysis_manager
		
		self.__stop_event = threading.Event()
		self.__current = []
		self.__changed = False
	
	def stop(self):
		self.__stop_event.set()
	
	def run(self):
		from db.crisees.models import Query
		
		while True:
			if self.__stop_event.isSet():
				break
			
			from_model = Query.objects.filter(active = True, event__active = True, event__sources__sys_name = self.source.sys_name)
			
			if len(self.__current) == len(from_model):
				for curr, fm in zip(self.__current, from_model):
					if (curr.query != fm.query):
						self.__current = from_model
						self.__changed = True
					elif (curr.operator != fm.operator):
						self.__current = from_model
			else:
				self.__current = from_model
				self.__changed = True
			
			sleep(1)
	
	def has_changed(self):
		if self.__changed:
			self.__changed = False
			return True
		
		return False
	
	def is_empty(self):
		return not self.__current
	
	def get_list(self):
		return self.__current
	
	def get_list_str(self):
		return map(str, self.__current)
	
	def get_split_list_str(self):
		query_list = map(str, self.__current)
		new_list = []
		
		for query in query_list:
			separated = query.split(' ')
			count = 0
			
			if len(separated) > 1:
				for split_query in separated:
					new_list.append(split_query)
			else:
				new_list.append(query)
			
			count += 1
		
		return new_list
