#!/usr/bin/env python
# -*- coding: utf-8 -*-

from whoosh.index import create_in, open_dir, exists_in
from indexing.whoosh.schema import Schema
from indexing.base import Base
from shutil import rmtree
import os

INDEX_NAME = 'crisees.places.whoosh'

class Indexer(Base):
	def __init__(self, output):
		super(Indexer, self).__init__(output)
		self.index = self.get_index()
		self.writer = self.index.writer()
		self.count = 0
	
	def get_index(self):
		if os.path.exists(self.output):
			if exists_in(self.output, INDEX_NAME):
				return open_dir(self.output, indexname = INDEX_NAME)
			else:
				rmtree(self.output)
				os.mkdir(self.output)
				return create_in(self.output, Schema, indexname = INDEX_NAME)
		else:
			os.mkdir(self.output)
			return create_in(self.output, Schema, indexname = INDEX_NAME)
	
	def add(self, item):
		self.writer.update_document(**item)
		self.count += 1
		
		if self.count == 10000:
			self.writer.commit()
			self.writer = self.index.writer()
			self.count = 0
	
	def stop(self):
		self.writer.commit()
