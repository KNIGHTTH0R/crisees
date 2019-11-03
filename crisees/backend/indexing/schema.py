#!/usr/bin/env python
# -*- coding: utf-8 -*-

from whoosh.fields import *

class Schema(SchemaClass):
	item_id       = ID(stored = True, unique = True)
	event_id      = NUMERIC(stored = True)
	body          = TEXT(stored = True, spelling = True)
	creation_time = DATETIME(stored = True)
	indexing_time = DATETIME(stored = True)
	screen_name   = STORED
	geographical  = NUMERIC(stored = True)
	longitude     = STORED
	latitude      = STORED
	analysed      = BOOLEAN(stored = True)
	sentiment     = NUMERIC(stored = True, signed = True, decimal_places = 6)
