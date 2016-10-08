from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Game(models.model):
    gamePk = models.IntegerField(primary_key=True)
    homeTeam = models.ForeignKey()