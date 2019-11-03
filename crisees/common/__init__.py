#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os import getcwd

# For checking additions, after - before
# For checking removals, before - after
def list_difference(x, y):
	return list(set(x) - set(y))

def enum(**enums):
	return type('Enum', (), enums)

def get_project_root():
	return getcwd()
	
