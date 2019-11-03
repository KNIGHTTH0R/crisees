#!/usr/bin/env python
# -*- coding: utf-8 -*-

from whoosh.fields import *

class Schema(SchemaClass):
	item_id    = ID(unique = True)
	latitude   = NUMERIC(float, stored = True, decimal_places = 10)
	longitude  = NUMERIC(float, stored = True, decimal_places = 10)
	name       = TEXT(stored = True, spelling = True)
	place_type = TEXT(stored = True)
