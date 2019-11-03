#!/usr/bin/env python
# -*- coding: utf-8 -*-

from index.indexing.schemas.geo import Schema
from index.indexing.reader import Reader
from index.indexing.indexer import Index_Types
from math import sqrt

'''
Looks at the item and computes a sentiment value.
Basic right now. Looking to improve this.
'''
def parse(scanner, item):
	sentiment_dict = scanner.analysis_manager.sentiment_dict
	sentiment_pattern = scanner.analysis_manager.sentiment_pattern
	
	if sentiment_dict is not None and len(sentiment_dict) > 0:
		words = sentiment_pattern.split(item['body'].lower())
		sentiments = map(lambda word: sentiment_dict.get(word, 0), words)
		
		if sentiments:
			item['sentiment'] = float(sum(sentiments)) / sqrt(len(sentiments))
		else:
			item['sentiment'] = 0
	
	return item
