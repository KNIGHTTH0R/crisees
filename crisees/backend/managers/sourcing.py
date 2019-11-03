#!/usr/bin/env python
# -*- coding: utf-8 -*-

from time import sleep
from common import list_difference, get_project_root
from common.terminal import statuses
from backend.sourcing.scanner import Scanner
import os

class Sourcing(object):
	
	def __init__(self, analysis_manager):
		self.__analysis_manager = analysis_manager
		self.__current = {}
		self.__failed = []
	
	def stop(self):
		for source in self.__current.keys():
			self.__stop_source(source, stop_scanner = True)
		
		print statuses.success("Sourcing manager successfully terminated.")
	
	def start(self):
		from db.crisees.models import Source
		
		while True:
			from_model = Source.objects.filter(active = True)
			
			additions = list_difference(from_model, self.__current)
			removals = list_difference(self.__current, from_model)
			
			for source in additions:
				self.__add(source)
			
			for source in removals:
				self.__remove(source)
			
			for source in self.__current.keys():
				self.__indexer_check(source)
			
			sleep(5)
	
	def __add(self, source):
		if source not in self.__failed:
			if os.path.exists(os.path.join(get_project_root(), ('backend/specific/%s.py' % source.sys_name))):
				module_import = __import__(('backend.specific.%s' % source.sys_name), fromlist = ['backend.specific'])
				
				try:
					module_import.SETTINGS
					module_import.Schema
					module_import.Collector
					
					scanner = Scanner(source, self.__analysis_manager)
					scanner.start()
					
					self.__current[source] ={
						'import'  : module_import,
						'threads' : {'scanner': scanner},
						'children': False,
					}
					
					print statuses.success("%s has started." % str(source))
				except AttributeError:
					self.__specific_invalid(source)
			else:
				self.__specific_invalid(source)
	
	def __specific_invalid(self, source):
		self.__failed.append(source)
		
		print statuses.fail(
			("The source %s has failed." % str(source)),
			sub = ("Check to see if %s has a valid specifics script." % str(source)))
	
	def __fail(self, source):
		self.__failed.append(source)
		
		print statuses.fail(
			("The source %s has failed." % str(source)),
			sub = "This could be a failure to start, or another runtime problem.")
	
	def __remove(self, source, emergency_stop = False):
		self.__stop_source(source, emergency_stop = emergency_stop)
		del self.__current[source]
		
		print statuses.info("%s has stopped." % str(source))
	
	def __stop_source(self, source, stop_scanner = True, emergency_stop = False):
		current_source = self.__current[source]
		threads = current_source['threads']
		
		if emergency_stop:
			threads['scanner'].stop()
			threads['collector'].crisis_stop()
		else:
			if stop_scanner:
				print statuses.alert(
					"Request to stop %s received." % str(source),
					sub = "Please allow time for the associated threads to finish.")
				
				threads['scanner'].stop()
			
			if 'collector' in threads:
				threads['collector'].stop()
				threads['collector'].join()
				
				if threads['collector'].filterer.isAlive():
					threads['collector'].filterer.join()
				
				if threads['collector'].filterer.indexer.isAlive():
					threads['collector'].filterer.indexer.join()
				
				if threads['collector'].filterer.indexer.analyser.isAlive():
					threads['collector'].filterer.indexer.analyser.join()
				
				del threads['collector']
				current_source['children'] = False
			
			if stop_scanner:
				threads['scanner'].join()
	
	def __indexer_check(self, source):
		current_source = self.__current[source]
		threads = current_source['threads']
		
		if threads['scanner'].is_empty():
			if 'collector' in threads:
				self.__stop_source(source, stop_scanner = False)
		else:
			if 'collector' not in threads:
				collector = current_source['import'].Collector(threads['scanner'])
				collector.start()
				
				threads['collector'] = collector
		
		if 'collector' in threads:
			if current_source['children']:
				if not self.__check_threads(source):
					self.__remove(source, emergency_stop = True)
					self.__fail(source)
			else:
				if threads['collector'].isAlive():
					threads['filterer'] = threads['collector'].filterer
					threads['indexer'] = threads['collector'].filterer.indexer
					threads['analyser'] = threads['collector'].filterer.indexer.analyser
					
					current_source['children'] = True
				else:
					self.__remove(source, emergency_stop = True)
					self.__fail(source)
	
	def __check_threads(self, source):
		threads = self.__current[source]['threads']
		
		for thread in threads:
			if not threads[thread].isAlive():
				return False
		
		return True
