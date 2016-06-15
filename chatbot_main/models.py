from __future__ import unicode_literals

from django.db import models

class HackerEarth_DB(models.Model):
	contest_name = models.CharField(max_length=100)
	contest_url  = models.CharField(max_length=300)
	contest_end_time = models.DateTimeField()
	contest_gather_time = models.DateTimeField()
 
class CodeChef_DB(models.Model):
	contest_name = models.CharField(max_length=100)
	contest_url  = models.CharField(max_length=300)
	contest_end_time = models.DateTimeField()
	contest_gather_time = models.DateTimeField()

class LastFetch(models.Model):
	update_date = models.DateTimeField()

class Message_Log(models.Model):
	userid = models.BigIntegerField()
	msg_date = models.DateTimeField()
	msg = models.CharField(max_length=100)