#!/usr/bin/env python
# -*- coding: utf-8 -*-

from common import enum
import os

Colours = enum(
	Default = 0,
	Red     = 31,
	Yellow  = 33,
	Green   = 32,
	Blue    = 34,
	Cyan    = 36,
	Magenta = 35)

Welcome_Styles = enum(
	Default = 0,
	Backend = 1,
	Api     = 2,
	Web     = 3,
	Startup = 4)

def clear(lines = 100):
	if (os.name == 'posix'):
		os.system('clear')
	elif (os.name in ('nt', 'dos', 'ce')):
		os.system('cls')
	else:
		print '\n' * lines

def highlight(string, colour = Colours.Default, bold = False):
	attr = []
	
	try:
		attr.append(str(colour))
	except AttributeError:
		attr.append(str(Colours.Default))
	
	if bold:
		attr.append('1')
	
	return '\x1b[%sm%s\x1b[0m' % (';'.join(attr), string)

def status(main, sub = "", colour = Colours.Default):
	string = highlight(u" • " + main, colour, True)
	
	if sub != '':
		string = string + "\n" + highlight("   " + sub, colour, False)
	
	return string

def print_welcome(style = Welcome_Styles.Default):
	clear()
	print highlight("Welcome to Cri", Colours.Cyan, True) + highlight("see", Colours.Yellow, True) + highlight("s!", Colours.Cyan, True)
	
	if style == Welcome_Styles.Backend:
		print highlight("Data Sourcing Backend", Colours.Cyan, True)
	elif style == Welcome_Styles.Api:
		print highlight("API", Colours.Cyan, True)
	elif style == Welcome_Styles.Web:
		print highlight("Web", Colours.Cyan, True)
	elif style == Welcome_Styles.Startup:
		print highlight("Startup Checks", Colours.Cyan, True)
	
	print
