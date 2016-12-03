from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.http import Http404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from team.models import Team
from player.models import Player, PlayerGameFilterStats
from playbyplay.models import Game
from datetime import date, datetime
from playbyplay.forms import GameFilterForm, GameForm

import playerqueries

from fancystats import toi, corsi


def players(request):
    teamstrength = "all"
    scoresituation = "all"
    period = "all"
    currentSeason = Game.objects.latest("endDateTime").season
    seasons = [currentSeason, ]
    form = GameFilterForm()
    startDate = None
    endDate = None
    venues = []
    teams = []
    if request.method == 'GET':
        form = GameFilterForm(request.GET)
        if form.is_valid():
            cd = form.cleaned_data
            teamstrength = cd["teamstrengths"]
            scoresituation = cd["scoresituation"]
            period = cd["period"]
            startDate = cd["startDate"]
            endDate = cd["endDate"]
            venues = cd["venues"]
            teams = cd["teams"]
            seasons = [cd["season"], ]
            if len(seasons) == 0:
                seasons = [currentSeason, ]
    gameids = Game.objects.values_list("gamePk", flat=True).filter(gameState__in=[5, 6, 7])
    if startDate is not None:
        gameids = gameids.filter(dateTime__date__gte=startDate)
    if endDate is not None:
        gameids = gameids.filter(dateTime__date__lte=endDate)
    if len(venues) > 0:
        gameids = gameids.filter(venue__in=venues)
    if len(teams) > 0:
        gameids = gameids.filter(Q(homeTeam__in=cd['teams']) | Q(awayTeam__in=cd['teams']))
    gameids = [x for x in gameids]
    pgs = PlayerGameFilterStats.objects.raw(playerqueries.playersquery, [seasons, gameids, scoresituation, teamstrength, period])

    stats = {}
    for row in pgs:
        season = row.season
        playerid = row.player_id
        if playerid not in stats:
            stats[playerid] = {}
        if season not in stats[playerid]:
            stats[playerid][season] = row.__dict__
            stats[playerid][season]["games"] = 1
            stats[playerid][season].pop("_state", None)
            stats[playerid][season].pop("game_id", None)
            stats[playerid][season].pop("period", None)
            stats[playerid][season].pop("teamstrength", None)
            stats[playerid][season].pop("scoresituation", None)
            stats[playerid][season].pop("player_id", None)
        else:
            stats[playerid][season]["games"] += 1
            for key in stats[playerid][season]:
                if key not in ["abbreviation", "teamName", "shortName", "fullName"]:
                    try:
                        stats[playerid][season][key] += row.__dict__[key]
                    except:
                        pass
                elif key == "abbreviation":
                    if stats[playerid][season][key] != row.__dict__[key]:
                        stats[playerid][season][key] += u", {}".format(row.__dict__[key])
                elif key == "teamName":
                    if stats[playerid][season][key] != row.__dict__[key]:
                        stats[playerid][season][key] += u", {}".format(row.__dict__[key])
                elif key == "shortName":
                    if stats[playerid][season][key] != row.__dict__[key]:
                        stats[playerid][season][key] += u", {}".format(row.__dict__[key])
    for playerid in stats:
        for season in stats[playerid]:
            row = stats[playerid][season]
            row["toi"] = toi.format_minutes(row["toi"] / row["games"])
            row["fo"] = '%.2f' % corsi.corsi_percent(row["fo_w"], row["fo_l"])
            row["sf"] = '%.2f' % corsi.corsi_percent(row["shotsFor"], row["shotsAgainst"])
            row["msf"] = '%.2f' % corsi.corsi_percent(row["missedShotsFor"],
                row["missedShotsAgainst"])
            row["bsf"] = '%.2f' % corsi.corsi_percent(row["blockedShotsFor"],
                row["blockedShotsAgainst"])
            row["gf"] = '%.2f' % corsi.corsi_percent(row["goalsFor"], row["goalsAgainst"])
            row["cf"] = '%.2f' % corsi.corsi_percent(row["corsiFor"], row["corsiAgainst"])
            row["ff"] = '%.2f' % corsi.corsi_percent(row["fenwickFor"], row["fenwickAgainst"])
            row["hit"] = '%.2f' % corsi.corsi_percent(row["hitFor"], row["hitAgainst"])
            row["pn"] = '%.2f' % corsi.corsi_percent(row["penaltyFor"], row["penaltyAgainst"])
            row["scf"] = '%.2f' % corsi.corsi_percent(row["scoringChancesFor"], row["scoringChancesAgainst"])
            row["hscf"] = '%.2f' % corsi.corsi_percent(row["highDangerScoringChancesFor"], row["highDangerScoringChancesAgainst"])
            if row["neutralZoneStarts"] is not None:
                row["zso"] = '%.2f' % corsi.corsi_percent(row["offensiveZoneStarts"], row["neutralZoneStarts"] + row["defensiveZoneStarts"])
            else:
                row["zso"] = "0.0"

    context = {}
    context["form"] = form
    context["stats"] = stats
    return render(request, 'players/players.html', context)

def player_page(request, player_id):
    player = get_object_or_404(Player, id=player_id)
    teamstrength = "all"
    scoresituation = "all"
    period = "all"
    currentSeason = Game.objects.latest("endDateTime").season
    seasons = [currentSeason, ]
    form = GameFilterForm()
    startDate = None
    endDate = None
    venues = []
    teams = []
    if request.method == 'GET':
        form = GameFilterForm(request.GET)
        if form.is_valid():
            cd = form.cleaned_data
            teamstrength = cd["teamstrengths"]
            scoresituation = cd["scoresituation"]
            period = cd["period"]
            startDate = cd["startDate"]
            endDate = cd["endDate"]
            venues = cd["venues"]
            teams = cd["teams"]
            seasons = [cd["season"], ]
            if len(seasons) == 0:
                seasons = [currentSeason, ]
    gameids = Game.objects.values_list("gamePk", flat=True).filter(gameState__in=[5, 6, 7])
    if startDate is not None:
        gameids = gameids.filter(dateTime__date__gte=startDate)
    if endDate is not None:
        gameids = gameids.filter(dateTime__date__lte=endDate)
    if len(venues) > 0:
        gameids = gameids.filter(venue__in=venues)
    if len(teams) > 0:
        gameids = gameids.filter(Q(homeTeam__in=cd['teams']) | Q(awayTeam__in=cd['teams']))
    gameids = [x for x in gameids]
    pgs = PlayerGameFilterStats.objects.raw(playerqueries.playerquery, [seasons, gameids, scoresituation, teamstrength, period, player.id])
    stats = {}
    for row in pgs:
        season = row.season
        playerid = player.id
        if playerid not in stats:
            stats[playerid] = {}
        if season not in stats[playerid]:
            stats[playerid][season] = row.__dict__
            stats[playerid][season]["games"] = 1
            stats[playerid][season].pop("_state", None)
            stats[playerid][season].pop("game_id", None)
            stats[playerid][season].pop("period", None)
            stats[playerid][season].pop("teamstrength", None)
            stats[playerid][season].pop("scoresituation", None)
            stats[playerid][season].pop("player_id", None)
        else:
            stats[playerid][season]["games"] += 1
            for key in stats[playerid][season]:
                if key not in ["abbreviation", "teamName", "shortName"]:
                    try:
                        stats[playerid][season][key] += row.__dict__[key]
                    except:
                        pass
                elif key == "abbreviation":
                    if stats[playerid][season][key] != row.__dict__[key]:
                        stats[playerid][season][key] += u", {}".format(row.__dict__[key])
                elif key == "teamName":
                    if stats[playerid][season][key] != row.__dict__[key]:
                        stats[playerid][season][key] += u", {}".format(row.__dict__[key])
                elif key == "shortName":
                    if stats[playerid][season][key] != row.__dict__[key]:
                        stats[playerid][season][key] += u", {}".format(row.__dict__[key])
    for playerid in stats:
        for season in stats[playerid]:
            row = stats[playerid][season]
            row["toi"] = toi.format_minutes(row["toi"] / row["games"])
            row["fo"] = '%.2f' % corsi.corsi_percent(row["fo_w"], row["fo_l"])
            row["sf"] = '%.2f' % corsi.corsi_percent(row["shotsFor"], row["shotsAgainst"])
            row["msf"] = '%.2f' % corsi.corsi_percent(row["missedShotsFor"],
                row["missedShotsAgainst"])
            row["bsf"] = '%.2f' % corsi.corsi_percent(row["blockedShotsFor"],
                row["blockedShotsAgainst"])
            row["gf"] = '%.2f' % corsi.corsi_percent(row["goalsFor"], row["goalsAgainst"])
            row["cf"] = '%.2f' % corsi.corsi_percent(row["corsiFor"], row["corsiAgainst"])
            row["ff"] = '%.2f' % corsi.corsi_percent(row["fenwickFor"], row["fenwickAgainst"])
            row["hit"] = '%.2f' % corsi.corsi_percent(row["hitFor"], row["hitAgainst"])
            row["pn"] = '%.2f' % corsi.corsi_percent(row["penaltyFor"], row["penaltyAgainst"])
            row["scf"] = '%.2f' % corsi.corsi_percent(row["scoringChancesFor"], row["scoringChancesAgainst"])
            row["hscf"] = '%.2f' % corsi.corsi_percent(row["highDangerScoringChancesFor"], row["highDangerScoringChancesAgainst"])
            if row["neutralZoneStarts"] is not None:
                row["zso"] = '%.2f' % corsi.corsi_percent(row["offensiveZoneStarts"], row["neutralZoneStarts"] + row["defensiveZoneStarts"])
            else:
                row["zso"] = 0

    context = {}
    context["player"] = player
    context["form"] = form
    context["stats"] = stats
    return render(request, 'players/player_page.html', context)
