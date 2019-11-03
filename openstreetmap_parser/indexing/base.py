#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Base(object):
	def __init__(self, output):
		self.output = output
	
	def add(self, item):
		raise NotImplementedError
	
	def stop(self):
		raise NotImplementedError
	
	
