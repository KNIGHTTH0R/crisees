#!/usr/bin/env python
# -*- coding: utf-8 -*-

from index.indexing.indexer import Indexer
from whoosh.filedb.multiproc import MultiSegmentWriter

class Writer(Indexer):
	
	def __init__(self, schema, name, index_type, commit_count = 5):
		super(Writer, self).__init__(schema, name, index_type)
		self.__commit_count = commit_count
		
		self.writer = self.get_writer()
		self.__count = 0
		self.__isMultiSegment = False
	
	def get_writer(self):
		return self.index.writer()
	
	def set_multiSegmentWriter(self, limitmb = 128, procs = 4):
		self.__isMultiSegment = True
		self.writer = MultiSegmentWriter(self.index, limitmb, procs)
	
	def save(self, item):
		self.writer.update_document(**item)
		self.__count += 1
		
		if not self.__isMultiSegment and self.__count == self.__commit_count:
			self.commit()
			self.writer = self.get_writer()
			self.__count = 0
	
	def commit(self):
		self.writer.commit()
