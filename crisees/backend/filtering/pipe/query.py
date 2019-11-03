#!/usr/bin/env python
# -*- coding: utf-8 -*-

from string import punctuation, maketrans
from db.crisees.models import Event, Query
import re

def parse(scanner, item):
	events = Event.objects.filter(active = True, sources = scanner.source)
	punctuation = '!"$%&\'()*+,./:;<=>?[\]^_`{|}~'
	
	regex = re.compile(r'[%s]' % punctuation)
	text = regex.sub('', item['body']).lower()
	
	prev_or = False
	
	for event in events:
		queries = Query.objects.filter(active = True, event = event)
		
		if len(queries) == 0:
			continue
		
		query = generate_query_str(queries)
		prev_or = False
		
		for or_queries in query.split('OR'):
			prev_and = True
			and_queries = map(unicode.strip, or_queries.split('AND'))
			
			for word in and_queries:
				if word.startswith('NOT '):
					prev_and = True if re.search(r"\b%s\b" % re.escape(word[4:].lower()), text) == None else False
					
					if not prev_and:
						break
				else:
					prev_and = False if re.search(r"\b%s\b" % re.escape(word.lower()), text) == None else True
					
					if not prev_and:
						break
			
			prev_or = prev_or or prev_and
	
	if prev_or:
		item['event_id'] = event.id
		return item
	
	return None

def generate_query_str(query_list):
	return_str = ""
	counter = 1
	
	for query in query_list:
		if counter == len(query_list):
			if query.logical_not:
				return_str += "NOT " + query.query
			else:
				return_str += query.query
		else:
			if query.logical_not:
				return_str += "NOT " + query.query + " " + query.operator + " "
			else:
				return_str += query.query + " " + query.operator + " "
		
		counter += 1
	
	return return_str
