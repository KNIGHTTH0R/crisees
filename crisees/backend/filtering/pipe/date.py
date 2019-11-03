#!/usr/bin/env python
# -*- coding: utf-8 -*-

def parse(scanner, item):
	if 'since_time' in item:
		if item['creation_time'] < item['since_time'].replace(tzinfo = None):
			item = None
	
	return item
