from __future__ import unicode_literals

from django.db import models

import constants
from fancystats import constants as fconstants


class Venue(models.Model):
    name = models.CharField(max_length=50)
    city = models.CharField(max_length=50, null=True, blank=True)
    timeZone = models.CharField(max_length=50, null=True, blank=True)
    timeZoneOffset = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = ("name", "city")

    def __unicode__(self):
        if self.city is not None:
            return self.name + ", " + self.city
        return self.name


class TeamGameStats(models.Model):
    game = models.ForeignKey('playbyplay.Game')
    team = models.ForeignKey('team.Team')
    period = models.CharField(max_length=4, choices=fconstants.PERIOD_CHOICES, db_index=True)
    teamstrength = models.CharField(max_length=6, choices=fconstants.TEAMSTRENGTHS_CHOICES, db_index=True)
    scoresituation = models.CharField(max_length=6, choices=fconstants.SCORESITUATION_CHOICES, db_index=True)
    toi = models.IntegerField(blank=True, null=True)
    scoringChancesFor = models.IntegerField(blank=True, null=True)
    scoringChancesAgainst = models.IntegerField(blank=True, null=True)
    highDangerScoringChancesFor = models.IntegerField(blank=True, null=True)
    highDangerScoringChancesAgainst = models.IntegerField(blank=True, null=True)
    offensiveZoneStartsFor = models.IntegerField(blank=True, null=True)
    offensiveZoneStartsAgainst = models.IntegerField(blank=True, null=True)
    faceoffWins = models.IntegerField(blank=True, null=True)
    faceoffLosses = models.IntegerField(blank=True, null=True)
    shotsFor = models.IntegerField(blank=True, null=True)
    shotsAgainst = models.IntegerField(blank=True, null=True)
    missedShotsFor = models.IntegerField(blank=True, null=True)
    missedShotsAgainst = models.IntegerField(blank=True, null=True)
    blockedShotsFor = models.IntegerField(blank=True, null=True)
    blockedShotsAgainst = models.IntegerField(blank=True, null=True)
    goalsFor = models.IntegerField(blank=True, null=True)
    goalsAgainst = models.IntegerField(blank=True, null=True)
    penaltyFor = models.IntegerField(blank=True, null=True)
    penaltyAgainst = models.IntegerField(blank=True, null=True)
    giveaways = models.IntegerField(blank=True, null=True)
    takeaways = models.IntegerField(blank=True, null=True)
    hitsFor = models.IntegerField(blank=True, null=True)
    hitsAgainst = models.IntegerField(blank=True, null=True)
    corsiFor = models.IntegerField(blank=True, null=True)
    corsiAgainst = models.IntegerField(blank=True, null=True)


class Team(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    shortName = models.CharField(max_length=50)
    link = models.URLField()
    venue = models.ForeignKey(Venue)
    abbreviation = models.CharField(max_length=3)
    teamName = models.CharField(max_length=50)
    locationName = models.CharField(max_length=50)
    firstYearOfPlay = models.IntegerField()
    conference = models.CharField(max_length=1, choices=constants.conferences)
    division = models.CharField(max_length=1, choices=constants.divisions)
    officialSiteUrl = models.URLField()
    active = models.BooleanField(default=True)

    def __unicode__(self):
        return self.name


class SeasonStats(models.Model):
    date = models.DateField()
    team = models.ForeignKey(Team)
    season = models.IntegerField()
    goalsAgainst = models.IntegerField(null=True, blank=True)
    goalsScored = models.IntegerField(null=True, blank=True)
    points = models.IntegerField()
    gamesPlayed = models.IntegerField()
    streakCode = models.CharField(max_length=3, null=True, blank=True)
    wins = models.IntegerField()
    losses = models.IntegerField()
    ot = models.IntegerField()

    class Meta:
        unique_together = ("date", "team")
