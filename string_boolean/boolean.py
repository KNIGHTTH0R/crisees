#!/usr/bin/env python
# -*- coding: utf-8 -*-

from re import search, escape

query = u"world AND NOT cup"
term  = u"world cup"

prev_or = False

for or_queries in query.split('OR'):
	prev_and = True
	and_queries = map(unicode.strip, or_queries.split('AND'))
	
	for word in and_queries:
		if word.startswith('NOT '):
			prev_and = True if search(r"\b%s\b" % escape(word[4:].lower()), term.lower()) == None else False
			
			if not prev_and:
				break
		else:
			prev_and = False if search(r"\b%s\b" % escape(word.lower()), term.lower()) == None else True
			
			if not prev_and:
				break
	
	prev_or = prev_or or prev_and

print "Result: " + str(prev_or)
