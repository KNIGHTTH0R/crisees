#!/usr/bin/env python
# -*- coding: utf-8 -*-

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db/sqlite3.db'
    },
}

TIME_ZONE = 'Europe/London'

INSTALLED_APPS = (
    'db.crisees',
)
