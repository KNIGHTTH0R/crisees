#!/usr/bin/env python
# -*- coding: utf-8 -*-

from common import terminal

def fail(main, sub = ""):
	return terminal.status(main, sub = sub, colour = terminal.Colours.Red)

def success(main, sub = ""):
	return terminal.status(main, sub = sub, colour = terminal.Colours.Green)

def warning(main, sub = ""):
	return terminal.status(main, sub = sub, colour = terminal.Colours.Yellow)

def info(main, sub = ""):
	return terminal.status(main, sub = sub, colour = terminal.Colours.Blue)

def alert(main, sub = ""):
	return terminal.status(main, sub = sub, colour = terminal.Colours.Magenta)
