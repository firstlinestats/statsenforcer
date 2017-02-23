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


class GoalieGameFilterStats(models.Model):
    player = models.ForeignKey(Player)
    game = models.ForeignKey('playbyplay.Game')
    team = models.ForeignKey('team.Team')
    period = models.CharField(max_length=4, choices=fconstants.PERIOD_CHOICES, db_index=True)
    teamstrength = models.CharField(max_length=6, choices=fconstants.TEAMSTRENGTHS_CHOICES, db_index=True)
    scoresituation = models.CharField(max_length=6, choices=fconstants.SCORESITUATION_CHOICES, db_index=True)
    toi = models.IntegerField(blank=True, null=True)
    savesUnknown = models.IntegerField(blank=True, null=True)
    goalsUnknown = models.IntegerField(blank=True, null=True)
    savesLow = models.IntegerField(blank=True, null=True)
    goalsLow = models.IntegerField(blank=True, null=True)
    savesMedium = models.IntegerField(blank=True, null=True)
    goalsMedium = models.IntegerField(blank=True, null=True)
    savesHigh = models.IntegerField(blank=True, null=True)
    goalsHigh = models.IntegerField(blank=True, null=True)


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
    scoringChancesFor = models.IntegerField(blank=True, null=True)
    scoringChancesAgainst = models.IntegerField(blank=True, null=True)
    highDangerScoringChancesFor = models.IntegerField(blank=True, null=True)
    highDangerScoringChancesAgainst = models.IntegerField(blank=True, null=True)
    individualShotsBlocked = models.IntegerField(blank=True, null=True)
    offensiveZoneStarts = models.IntegerField(blank=True, null=True)
    neutralZoneStarts = models.IntegerField(blank=True, null=True)
    defensiveZoneStarts = models.IntegerField(blank=True, null=True)
    shotsFor = models.IntegerField(blank=True, null=True)
    shotsAgainst = models.IntegerField(blank=True, null=True)
    missedShotsFor = models.IntegerField(blank=True, null=True)
    missedShotsAgainst = models.IntegerField(blank=True, null=True)
    blockedShotsFor = models.IntegerField(blank=True, null=True)
    blockedShotsAgainst = models.IntegerField(blank=True, null=True)
    individualShots = models.IntegerField(blank=True, null=True)
    individualMissedShots = models.IntegerField(blank=True, null=True)
    individualBlockedShots = models.IntegerField(blank=True, null=True)
    individualScoringChances = models.IntegerField(blank=True, null=True)
    individualHighDangerScoringChances = models.IntegerField(blank=True, null=True)


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

class PrecalcPlayerGameFilterStats(models.Model):
    assists1 = models.IntegerField(null=True)
    assists2 = models.IntegerField(null=True)
    blockedShotsAgainst = models.IntegerField(db_column='blockedShotsAgainst', null=True)
    blockedShotsFor = models.IntegerField(db_column='blockedShotsFor', null=True)
    corsiAgainst = models.IntegerField(db_column='corsiAgainst', null=True)
    corsiFor = models.IntegerField(db_column='corsiFor', null=True)
    defensiveZoneStarts = models.IntegerField(db_column='defensiveZoneStarts', null=True)
    fenwickAgainst = models.IntegerField(db_column='fenwickAgainst', null=True)
    fenwickFor = models.IntegerField(db_column='fenwickFor', null=True)
    fo_l = models.IntegerField(null=True)
    fo_w = models.IntegerField(null=True)
    game = models.IntegerField(null=True)
    goals = models.IntegerField(null=True)
    goalsAgainst = models.IntegerField(db_column='goalsAgainst', null=True)
    goalsFor = models.IntegerField(db_column='goalsFor', null=True)
    highDangerScoringChancesAgainst = models.IntegerField(db_column='highDangerScoringChancesAgainst', null=True)
    highDangerScoringChancesFor = models.IntegerField(db_column='highDangerScoringChancesFor', null=True)
    hitAgainst = models.IntegerField(db_column='hitAgainst', null=True)
    hitFor = models.IntegerField(db_column='hitFor', null=True)
    individualBlockedShots = models.IntegerField(db_column='individualBlockedShots', null=True)
    individualHighDangerScoringChances = models.IntegerField(db_column='individualHighDangerScoringChances', null=True)
    individualMissedShots = models.IntegerField(db_column='individualMissedShots', null=True)
    individualScoringChances = models.IntegerField(db_column='individualScoringChances', null=True)
    individualShots = models.IntegerField(db_column='individualShots', null=True)
    individualShotsBlocked = models.IntegerField(db_column='individualShotsBlocked', null=True)
    missedShotsAgainst = models.IntegerField(db_column='missedShotsAgainst', null=True)
    missedShotsFor = models.IntegerField(db_column='missedShotsFor', null=True)
    neutralZoneStarts = models.IntegerField(db_column='neutralZoneStarts', null=True)
    offensiveZoneStarts = models.IntegerField(db_column='offensiveZoneStarts', null=True)
    penaltyAgainst = models.IntegerField(db_column='penaltyAgainst', null=True)
    penaltyFor = models.IntegerField(db_column='penaltyFor', null=True)
    period = models.CharField(max_length=10, db_index=True)
    player = models.IntegerField(db_column='player_id')
    points = models.IntegerField(null=True)
    scoresituation = models.CharField(max_length=10, db_index=True)
    scoringChancesAgainst = models.IntegerField(db_column='scoringChancesAgainst', null=True)
    scoringChancesFor = models.IntegerField(db_column='scoringChancesFor', null=True)
    shotsAgainst = models.IntegerField(db_column='shotsAgainst', null=True)
    shotsFor = models.IntegerField(db_column='shotsFor', null=True)
    team = models.IntegerField(null=True)
    toi = models.IntegerField(null=True)

    class Meta:
        db_table = 'precalc_historical'

class PlayersPrecalc(models.Model):
    fullName = models.CharField(max_length=200, null=True)
    team = models.CharField(max_length=50, null=True)
    player = models.IntegerField(null=True)
    season = models.IntegerField(null=True, db_index=True)
    games = models.IntegerField(null=True)
    goals = models.IntegerField(null=True)
    assists1 = models.IntegerField(null=True)
    assists2 = models.IntegerField(null=True)
    points = models.IntegerField(null=True)
    p60 = models.FloatField(null=True)
    missedShotsAgainst = models.IntegerField(null=True)
    individualScoringChances = models.IntegerField(null=True)
    a60 = models.FloatField(null=True)
    defensiveZoneStarts = models.IntegerField(null=True)
    cf60 = models.FloatField(null=True)
    highDangerScoringChancesFor = models.IntegerField(null=True)
    scf = models.FloatField(null=True)
    scoringChancesAgainst = models.IntegerField(null=True)
    blockedShotsAgainst = models.IntegerField(null=True)
    fenwickAgainst = models.FloatField(null=True)
    hit = models.FloatField(null=True)
    shotsAgainst = models.IntegerField(null=True)
    individualMissedShots = models.IntegerField(null=True)
    hscf = models.FloatField(null=True)
    gf60 = models.FloatField(null=True)
    penaltyFor = models.IntegerField(null=True)
    goalsFor = models.IntegerField(null=True)
    bsf = models.FloatField(null=True)
    toi = models.IntegerField(null=True)
    hscf60 = models.FloatField(null=True)
    corsiAgainst = models.FloatField(null=True)
    individualShots = models.IntegerField(null=True)
    msf = models.FloatField(null=True)
    pn = models.FloatField(null=True)
    scoringChancesFor = models.IntegerField(null=True)
    goalsAgainst = models.IntegerField(null=True)
    blockedShotsFor = models.IntegerField(null=True)
    individualHighDangerScoringChances = models.IntegerField(null=True)
    hitAgainst = models.IntegerField(null=True)
    zso = models.FloatField(null=True)
    cf = models.FloatField(null=True)
    individualBlockedShots = models.IntegerField(null=True)
    ff = models.FloatField(null=True)
    offensiveZoneStarts = models.IntegerField(null=True)
    a160 = models.FloatField(null=True)
    corsiFor = models.FloatField(null=True)
    penaltyAgainst = models.IntegerField(null=True)
    fo = models.FloatField(null=True)
    highDangerScoringChancesAgainst = models.IntegerField(null=True)
    neutralZoneStarts = models.IntegerField(null=True)
    individualShotsBlocked = models.IntegerField(null=True)
    gf = models.FloatField(null=True)
    ff60 = models.FloatField(null=True)
    fo_w = models.FloatField(null=True)
    shotsFor = models.IntegerField(null=True)
    fo_l = models.FloatField(null=True)
    hitFor = models.IntegerField(null=True)
    missedShotsFor = models.IntegerField(null=True)
    scf60 = models.FloatField(null=True)
    fenwickFor = models.FloatField(null=True)
    sf = models.FloatField(null=True)
    scoresituation = models.CharField(max_length=50, null=True, db_index=True)
    teamstrength = models.CharField(max_length=50, null=True, db_index=True)
    period = models.CharField(max_length=50, null=True, db_index=True)

    class Meta:
        db_table = 'player_precalc'
