#!/usr/bin/env python
# -*- coding: utf-8 -*-

from common import terminal

def backend():
	terminal.print_welcome(terminal.Welcome_Styles.Backend)

def api():
	terminal.print_welcome(terminal.Welcome_Styles.Api)

def web():
	terminal.print_welcome(terminal.Welcome_Styles.Web)

def startup():
	terminal.print_welcome(terminal.Welcome_Styles.Startup)
