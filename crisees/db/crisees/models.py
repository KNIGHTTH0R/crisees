#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db import models

STR_LENGTH = 200

OPERATOR_CHOICES = (
	('AND', 'Logical AND'),
	('OR', 'Logical OR'),
)

BACKEND_CHOICES = (
    ('FILTER', 'Filter pipe'),
    ('ANALYSIS', 'Analysis pipe'),
)

class Source(models.Model):
	sys_name       = models.CharField(max_length = STR_LENGTH, primary_key=True)
	name           = models.CharField(max_length = STR_LENGTH)
	active         = models.BooleanField()
	
	def __unicode__(self):
		return self.name
	
	class Meta:
		verbose_name        = "source"
		verbose_name_plural = "sources"
		ordering            = ('name', )

class Event(models.Model):
	name           = models.CharField(max_length = STR_LENGTH)
	active         = models.BooleanField()
	created        = models.DateTimeField()
	sources        = models.ManyToManyField(Source)
	longitude      = models.CharField(max_length = STR_LENGTH)
	latitude       = models.CharField(max_length = STR_LENGTH)
	distance       = models.PositiveIntegerField(default = 5)
	
	def __unicode__(self):
		return self.name
	
	class Meta:
		verbose_name        = "event"
		verbose_name_plural = "events"
		ordering            = ('name', )

class Query(models.Model):
	event          = models.ForeignKey(Event)
	query          = models.CharField(max_length = STR_LENGTH)
	step           = models.PositiveIntegerField(default = 1)
	operator       = models.CharField(max_length = 3, choices = OPERATOR_CHOICES, default = 'OR')
	created        = models.DateTimeField()
	active         = models.BooleanField()
	logical_not    = models.BooleanField()
	
	def __unicode__(self):
		return self.query
	
	class Meta:
		verbose_name        = "query term"
		verbose_name_plural = "query terms"
		ordering            = ('event', 'step', )

class Backend(models.Model):
	sys_name       = models.CharField(max_length = STR_LENGTH, primary_key=True)
	name           = models.CharField(max_length = STR_LENGTH)
	description    = models.CharField(max_length = STR_LENGTH)
	pipe           = models.CharField(max_length = 8, choices = BACKEND_CHOICES, default = 'FILTER')
	
	def __unicode__(self):
		return self.name
	
	class Meta:
		verbose_name        = "backend module"
		verbose_name_plural = "backend modules"
		ordering            = ('name', 'pipe', )

class BackendOrder(models.Model):
	source         = models.ForeignKey(Source)
	backend_module = models.ForeignKey(Backend)
	step           = models.PositiveIntegerField(default = 1)
	
	def __unicode__(self):
		return "%s and %s" % (self.source.name, self.backend_module.name)
	
	class Meta:
		verbose_name        = "backend module ordering rule"
		verbose_name_plural = "backend module ordering rules"
		ordering            = ('step', 'backend_module__pipe')

class BackendConfig_Filter_Query(models.Model):
	source         = models.ForeignKey(Source, unique = True)
	exact_match    = models.BooleanField(default = True)
	case_sensitive = models.BooleanField(default = False)
	
	def __unicode__(self):
		return self.source.name
	
	class Meta:
		verbose_name        = "backend query filter rule"
		verbose_name_plural = "backend query filter rules"
	
