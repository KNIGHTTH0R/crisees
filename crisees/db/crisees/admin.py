#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.contrib import admin
from django.contrib.auth.models import User, Group
from db.crisees.models import *

class QueryAdmin(admin.ModelAdmin):
	list_display = ('query', 'operator', 'event', 'created', 'active')

class Backend_Admin(admin.ModelAdmin):
	list_display = ('name', 'pipe', 'description')

class BackendOrder_Admin(admin.ModelAdmin):
	list_display = ('backend_module', 'source', 'step')

admin.site.register(Source)
admin.site.register(Event)
admin.site.register(Query, QueryAdmin)

admin.site.register(Backend, Backend_Admin)
admin.site.register(BackendOrder, BackendOrder_Admin)
admin.site.register(BackendConfig_Filter_Query)
