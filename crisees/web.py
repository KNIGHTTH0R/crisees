#!/usr/bin/env python
# -*- coding: utf-8 -*-

import common.startup
from django.core.management import execute_manager
from web import settings
from common.terminal import welcomes

# Imports Django settings, displays a welcome message, and launches the development server.
if __name__ == '__main__':
	welcomes.web()
	execute_manager(settings)
