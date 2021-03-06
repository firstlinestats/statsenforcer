from __future__ import unicode_literals

from django.db import models

from fancystats import constants


class Game(models.Model):
    gamePk = models.IntegerField(primary_key=True)
    link = models.URLField()
    gameType = models.CharField(max_length=2, choices=constants.gameTypes)
    season = models.IntegerField(db_index=True)
    dateTime = models.DateTimeField(null=True, blank=True, db_index=True)
    endDateTime = models.DateTimeField(null=True, blank=True)
    awayTeam = models.ForeignKey("team.Team", related_name="awayTeam")
    homeTeam = models.ForeignKey("team.Team", related_name="homeTeam")
    venue = models.ForeignKey("team.Venue")
    gameState = models.CharField(max_length=1, choices=constants.gameStates)
    homeScore = models.IntegerField(blank=True, null=True)
    awayScore = models.IntegerField(blank=True, null=True)
    homeShots = models.IntegerField(blank=True, null=True)
    awayShots = models.IntegerField(blank=True, null=True)
    homePPGoals = models.IntegerField(blank=True, null=True)
    awayPPGoals = models.IntegerField(blank=True, null=True)
    homePPOpportunities = models.IntegerField(blank=True, null=True)
    awayPPOpportunities = models.IntegerField(blank=True, null=True)
    homeFaceoffPercentage = models.DecimalField(decimal_places=2, max_digits=5, null=True, blank=True)
    awayFaceoffPercentage = models.DecimalField(decimal_places=2, max_digits=5, null=True, blank=True)
    homeBlocked = models.IntegerField(blank=True, null=True)
    awayBlocked = models.IntegerField(blank=True, null=True)
    homeMissed = models.IntegerField(blank=True, null=True)
    awayMissed = models.IntegerField(blank=True, null=True)
    homePIM = models.IntegerField(blank=True, null=True)
    awayPIM = models.IntegerField(blank=True, null=True)
    homeTakeaways = models.IntegerField(blank=True, null=True)
    awayTakeaways = models.IntegerField(blank=True, null=True)
    homeGiveaways = models.IntegerField(blank=True, null=True)
    awayGiveaways = models.IntegerField(blank=True, null=True)
    homeHits = models.IntegerField(blank=True, null=True)
    awayHits = models.IntegerField(blank=True, null=True)
    firstStar = models.ForeignKey("player.Player", null=True, blank=True, related_name="firstStar")
    secondStar = models.ForeignKey("player.Player", null=True, blank=True, related_name="secondStar")
    thirdStar = models.ForeignKey("player.Player", null=True, blank=True, related_name="thirdStar")

    # def __unicode__(self):
    #     if self.homeScore is not None:
    #         return self.homeTeam.name + " " + str(self.homeScore) + "-" + \
    #             str(self.awayScore) + " " + self.awayTeam.name + " " + str(self.dateTime)


class GamePeriod(models.Model):
    game = models.ForeignKey(Game)
    period = models.IntegerField()
    startTime = models.DateTimeField(null=True, blank=True)
    endTime = models.DateTimeField(null=True, blank=True)
    homeScore = models.IntegerField(null=True, blank=True)
    awayScore = models.IntegerField(null=True, blank=True)
    homeShots = models.IntegerField(null=True, blank=True)
    awayShots = models.IntegerField(null=True, blank=True)


class PlayByPlay(models.Model):
    id = models.IntegerField(primary_key=True)
    gamePk = models.ForeignKey(Game)
    eventId = models.IntegerField(null=True, blank=True)
    eventIdx = models.IntegerField(null=True, blank=True)
    period = models.IntegerField()
    periodTime = models.TimeField()
    dateTime = models.DateTimeField(null=True, blank=True)
    playType = models.CharField(max_length=25, choices=constants.playTypes)
    playDescription = models.CharField(max_length=100, null=True, blank=True)
    shotType = models.CharField(max_length=12, choices=constants.shotTypes, null=True, blank=True)
    penaltyType = models.CharField(max_length=100, null=True, blank=True)
    penaltySeverity = models.CharField(max_length=100, null=True, blank=True)
    penaltyMinutes = models.IntegerField(null=True, blank=True)
    homeScore = models.IntegerField()
    awayScore = models.IntegerField()
    xcoord = models.DecimalField(decimal_places=2, max_digits=5, null=True, blank=True)
    ycoord = models.DecimalField(decimal_places=2, max_digits=5, null=True, blank=True)
    timeOnIce = models.IntegerField(null=True, blank=True)
    strength = models.CharField(max_length=20, null=True, blank=True)
    team = models.ForeignKey("team.Team", null=True, blank=True)

    class Meta:
        verbose_name = "Play By Play"

    def __unicode__(self):
        return self.gamePk.homeTeam.shortName + " vs. " + self.gamePk.awayTeam.shortName + " on " + str(self.gamePk.dateTime) + " Play: " + str(self.eventId)


class PlayMedia(models.Model):
    game = models.ForeignKey(Game)
    play = models.IntegerField(null=True, blank=True, db_index=True)
    external_id = models.IntegerField(primary_key=True)
    mediatype = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    blurb = models.CharField(max_length=200)
    description = models.TextField()
    duration = models.CharField(max_length=200)
    image = models.ImageField(upload_to="preview", null=True, blank=True)

    class Meta:
        verbose_name = "Media Files"

    def __unicode__(self):
        return "Media for Game: {} and Play: {}".format(self.game.gamePk, self.play.id)


class PlayerGameStats(models.Model):
    player = models.ForeignKey("player.Player")
    game = models.ForeignKey(Game)
    team = models.ForeignKey("team.Team", null=True, blank=True)
    period = models.IntegerField(default=0)
    timeOnIce = models.TimeField(null=True, blank=True)
    assists = models.IntegerField(default=0)
    goals = models.IntegerField(default=0)
    shots = models.IntegerField(default=0)
    hits = models.IntegerField(default=0)
    powerPlayGoals = models.IntegerField(default=0)
    powerPlayAssists = models.IntegerField(default=0)
    penaltyMinutes = models.IntegerField(default=0)
    faceOffWins = models.IntegerField(default=0)
    faceoffTaken = models.IntegerField(default=0)
    takeaways = models.IntegerField(default=0)
    giveaways = models.IntegerField(default=0)
    shortHandedGoals = models.IntegerField(default=0)
    shortHandedAssists = models.IntegerField(default=0)
    blocked = models.IntegerField(default=0)
    plusMinus = models.IntegerField(default=0)
    evenTimeOnIce = models.TimeField(null=True, blank=True)
    powerPlayTimeOnIce = models.TimeField(null=True, blank=True)
    shortHandedTimeOnIce = models.TimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Player Game Stats"
        verbose_name_plural = "Players Game Stats"


class GoalieGameStats(models.Model):
    player = models.ForeignKey("player.Player")
    game = models.ForeignKey(Game)
    team = models.ForeignKey("team.Team")
    period = models.IntegerField()
    timeOnIce = models.TimeField()
    assists = models.IntegerField()
    goals = models.IntegerField()
    pim = models.IntegerField()
    shots = models.IntegerField()
    saves = models.IntegerField()
    powerPlaySaves = models.IntegerField()
    shortHandedSaves = models.IntegerField()
    evenSaves = models.IntegerField()
    shortHandedShotsAgainst = models.IntegerField()
    evenShotsAgainst = models.IntegerField()
    powerPlayShotsAgainst = models.IntegerField()
    decision = models.CharField(max_length=5)


class Shootout(models.Model):
    game = models.ForeignKey(Game)
    awayScores = models.IntegerField()
    awayAttempts = models.IntegerField()
    homeScores = models.IntegerField()
    homeAttempts = models.IntegerField()


class PlayerInPlay(models.Model):
    play = models.ForeignKey(PlayByPlay)
    game = models.ForeignKey(Game)
    player = models.ForeignKey("player.Player")
    player_type = models.IntegerField(null=True, blank=True,
                                      choices=constants.playerTypes)

    class Meta:
        verbose_name = "Player On Ice"
        verbose_name_plural = "Players On Ice"


class PlayerOnIce(models.Model):
    play = models.ForeignKey(PlayByPlay)
    game = models.ForeignKey(Game)
    player = models.ForeignKey("player.Player")

    class Meta:
        unique_together = ("play", "player", )


class GameScratch(models.Model):
    game = models.ForeignKey(Game)
    team = models.ForeignKey("team.Team")
    player = models.ForeignKey("player.Player")

    class Meta:
        verbose_name = "Game Scratch"
        verbose_name_plural = "Game Scratches"