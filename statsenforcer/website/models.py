from __future__ import unicode_literals

from django.db import models


class GlossaryTerm(models.Model):
    key = models.CharField(max_length=200, primary_key=True)
    value = models.TextField()
