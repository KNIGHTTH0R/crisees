#!/usr/bin/env python
# -*- coding: utf-8 -*-

from whoosh.index import create_in, open_dir, exists_in
from common import get_project_root
from common.terminal import statuses
from datetime import datetime
from shutil import rmtree
from common import enum
import os

Index_Types = enum(
	Source  = 0,
	Crisees = 1)

class Indexer(object):
	
	def __init__(self, schema, name, index_type):
		self.schema = schema
		self.name = name
		self.index_type = index_type
		
		self.index = self.open_index()
	
	def open_index(self):
		path_to_index = os.path.join(get_project_root(), 'index/whoosh')
		
		if self.index_type == Index_Types.Source:
			path_to_index = os.path.join(path_to_index, ('sources/%s.whoosh' % self.name))
		elif self.index_type == Index_Types.Crisees:
			path_to_index = os.path.join(path_to_index, ('crisees/%s.whoosh' % self.name))
		
		if os.path.exists(path_to_index):
			if exists_in(path_to_index, indexname = self.name):
				return open_dir(path_to_index, indexname = self.name)
			else:
				print statuses.warning(
					("Can't find a valid index at %s." % path_to_index),
					sub = "I'll recreate the index.")
				
				rmtree(path_to_index)
				os.mkdir(path_to_index)
				return create_in(path_to_index, self.schema, indexname = self.name)
		else:
			os.mkdir(path_to_index)
			return create_in(path_to_index, self.schema, indexname = self.name)

def index_exists(name, index_type):
	path_to_index = os.path.join(get_project_root(), 'index/whoosh')
	
	if index_type == Index_Types.Source:
		path_to_index = os.path.join(path_to_index, ('sources/%s.whoosh' % name))
	elif index_type == Index_Types.Crisees:
		path_to_index = os.path.join(path_to_index, ('crisees/%s.whoosh' % name))
	
	if os.path.exists(path_to_index):
		if exists_in(path_to_index, indexname = name):
			idx = open_dir(path_to_index, indexname = name)
			return idx.schema
	
	return False

def to_date(x):
	return datetime.strptime(x, "%a %b %d %H:%M:%S +0000 %Y")
