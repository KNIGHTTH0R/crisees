#!/usr/bin/env python
# -*- coding: utf-8 -*-

from whoosh.qparser import QueryParser
from index.indexing.indexer import Indexer

class Reader(Indexer):
	
	def __init__(self, schema, name, index_type):
		super(Reader, self).__init__(schema, name, index_type)
		self.reader = self.index.reader()
	
	def get_reader(self):
		return self.reader
	
	def get_searcher(self):
		return self.index.searcher()
	
	def get_queryparser(self, field):
		return QueryParser(field, self.schema)
	
	def refresh(self):
		self.reader = self.index.reader(reuse = self.reader)
