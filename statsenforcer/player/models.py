from __future__ import unicode_literals

from django.db import models

import constants

from fancystats import constants as fconstants


class Player(models.Model):
    id = models.IntegerField(primary_key=True)
    fullName = models.CharField(max_length=100, blank=True, null=True)
    link = models.URLField()
    firstName = models.CharField(max_length=50, blank=True, null=True)
    lastName = models.CharField(max_length=50, blank=True, null=True)
    primaryNumber = models.IntegerField(null=True, blank=True)
    primaryPositionCode = models.CharField(max_length=1, choices=constants.playerPositions, blank=True, null=True)
    birthDate = models.DateField(blank=True, null=True)
    birthCity = models.CharField(max_length=100, blank=True, null=True)
    birthStateProvince = models.CharField(max_length=100, blank=True, null=True)
    birthCountry = models.CharField(max_length=100, blank=True, null=True)
    height = models.CharField(max_length=10, blank=True, null=True)
    weight = models.IntegerField(blank=True, null=True)
    active = models.BooleanField(default=True)
    rookie = models.BooleanField(default=False)
    shootsCatches = models.CharField(max_length=1, blank=True, null=True)
    rosterStatus = models.CharField(max_length=1, choices=constants.rosterChoices, blank=True, null=True)
    currentTeam = models.ForeignKey("team.Team", blank=True, null=True)

    def __unicode__(self):
        return self.fullName


class PlayerGameFilterStats(models.Model):
    player = models.ForeignKey(Player)
    game = models.ForeignKey('playbyplay.Game')
    team = models.ForeignKey('team.Team')
    period = models.CharField(max_length=4, choices=fconstants.PERIOD_CHOICES, db_index=True)
    teamstrength = models.CharField(max_length=6, choices=fconstants.TEAMSTRENGTHS_CHOICES, db_index=True)
    scoresituation = models.CharField(max_length=6, choices=fconstants.SCORESITUATION_CHOICES, db_index=True)
    toi = models.IntegerField(blank=True, null=True)
    goals = models.IntegerField(blank=True, null=True)
    assists1 = models.IntegerField(blank=True, null=True)
    assists2 = models.IntegerField(blank=True, null=True)
    points = models.IntegerField(blank=True, null=True)
    corsiFor = models.IntegerField(blank=True, null=True)
    corsiAgainst = models.IntegerField(blank=True, null=True)
    fenwickFor = models.IntegerField(blank=True, null=True)
    fenwickAgainst = models.IntegerField(blank=True, null=True)
    goalsFor = models.IntegerField(blank=True, null=True)
    goalsAgainst = models.IntegerField(blank=True, null=True)
    fo_w = models.IntegerField(blank=True, null=True)
    fo_l = models.IntegerField(blank=True, null=True)
    hitFor = models.IntegerField(blank=True, null=True)
    hitAgainst = models.IntegerField(blank=True, null=True)
    penaltyFor = models.IntegerField(blank=True, null=True)
    penaltyAgainst = models.IntegerField(blank=True, null=True)



class CompiledPlayerGameStats(models.Model):
    player = models.ForeignKey(Player)
    game = models.ForeignKey("playbyplay.Game")
    period = models.IntegerField(db_index=True)
    strength = models.CharField(max_length=4, db_index=True)
    goals = models.IntegerField()  # Individual Goals
    assists = models.IntegerField()  # Individual Assists
    assists2 = models.IntegerField()  # Individual Sec. Assists
    gf = models.IntegerField()  # On-Ice Goals For
    ga = models.IntegerField()  # On-Ice Goals Against
    pnDrawn = models.IntegerField()
    pn = models.IntegerField()
    sf = models.IntegerField()  # Personal Shots For
    msf = models.IntegerField()  # Personal Missed Shots For
    bsf = models.IntegerField()  # Personal Blocked Shots For
    ab = models.IntegerField()  # Shot Attempts Blocked By Player
    onsf = models.IntegerField()  # On-Ice Shots For
    onmsf = models.IntegerField()  # On-Ice Missed Shots For
    onbsf = models.IntegerField()  # On-Ice Blocked Shots For
    offgf = models.IntegerField()  # Off-Ice Goals For
    offsf = models.IntegerField()  # Off-Ice Shots For
    offmsf = models.IntegerField()  # Off-Ice Missed Shots For
    offbsf = models.IntegerField()  # Off-Ice Blocked Shots For
    offga = models.IntegerField()  # Off-Ice Goals Against
    offsa = models.IntegerField()  # Off-Ice Shots Against
    offmsa = models.IntegerField()  # Off-Ice Missed Shots Against
    offbsa = models.IntegerField()  # Off-Ice Blocked Shots Against
    sa = models.IntegerField()  # Shots Against
    msa = models.IntegerField()  # Missed Shots Against
    bsa = models.IntegerField()  # Blocked Shots Against
    zso = models.IntegerField()  # Offensive Zone Starts
    zsn = models.IntegerField()  # Neutral Zone Starts
    zsd = models.IntegerField() # Defensive Zone Starts
    toi = models.TimeField()
    timeOffIce = models.TimeField()
    ihsc = models.IntegerField()  # Individual High-Danger Scoring Chances
    isc = models.IntegerField()  # Individual Scoring Chances
    sc = models.IntegerField()  # Scoring Chances
    hscf = models.IntegerField()  # High-Danger Scoring Chances
    hsca = models.IntegerField()  # HSC Against
    sca = models.IntegerField()  # SC Against
    fo_w = models.IntegerField()  # Faceoffs Won
    fo_l = models.IntegerField()  # Faceoffs Lost
    hit = models.IntegerField()  # Hits
    hitt = models.IntegerField()  # Hits Taken
    gv = models.IntegerField()  # Giveaways
    tk = models.IntegerField()  # Takeaways


class CompiledGoalieGameStats(models.Model):
    player = models.ForeignKey(Player)
    game = models.ForeignKey("playbyplay.Game")
    period = models.IntegerField(db_index=True)
    strength = models.CharField(max_length=4, db_index=True)
    shotsLow = models.IntegerField()
    savesLow = models.IntegerField()
    shotsMedium = models.IntegerField()
    savesMedium = models.IntegerField()
    shotsHigh = models.IntegerField()
    savesHigh = models.IntegerField()
    toi = models.TimeField()
