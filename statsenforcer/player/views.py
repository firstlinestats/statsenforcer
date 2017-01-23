from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.http import Http404, JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.serializers.json import DjangoJSONEncoder
from team.models import Team
from player.models import Player, PlayerGameFilterStats
from playbyplay.models import Game
from datetime import date, datetime
import json
import arrow
from playbyplay.forms import GameFilterForm, GameForm

import playerqueries

from fancystats import toi, corsi


def players(request):
    teamstrength = "even"
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
    pgs = PlayerGameFilterStats.objects.raw(playerqueries.newplayersquery, [seasons, gameids, scoresituation, teamstrength, period])

    teamnames = {}
    teams = Team.objects.all()
    for team in teams:
        teamnames[team.id] = team.abbreviation

    stats = []
    for playerid in pgs:
        row = playerid.__dict__
        row.pop("_state")
        toiSeconds = row["toi"]
        row["team"] = teamnames[row["team_id"]]
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
        row['gf60'] = '%.2f' % corsi.corsi_for_60(toiSeconds, row["goalsFor"])
        row['a60'] = '%.2f' % corsi.corsi_for_60(toiSeconds, row["assists1"] + row["assists2"])
        row['a160'] = '%.2f' % corsi.corsi_for_60(toiSeconds, row["assists1"])
        row['p60'] = '%.2f' % corsi.corsi_for_60(toiSeconds, row["points"])
        row['scf60'] = '%.2f' % corsi.corsi_for_60(toiSeconds, row["scoringChancesFor"])
        row['cf60'] = '%.2f' % corsi.corsi_for_60(toiSeconds, row["corsiFor"])
        row['ff60'] = '%.2f' % corsi.corsi_for_60(toiSeconds, row["fenwickFor"])
        row['hscf60'] = '%.2f' % corsi.corsi_for_60(toiSeconds, row["highDangerScoringChancesFor"])
        if row["neutralZoneStarts"] is not None:
            row["zso"] = '%.2f' % corsi.corsi_percent(row["offensiveZoneStarts"], row["neutralZoneStarts"] + row["defensiveZoneStarts"])
        else:
            row["zso"] = "0.0"
        stats.append(row)

    context = {}
    context["stats"] = stats
    if request.method == "GET" and "format" in request.GET and request.GET["format"] == "json":
        return JsonResponse(context)
    context["form"] = form
    context["statsJson"] = json.dumps(stats, cls=DjangoJSONEncoder)
    return render(request, 'players/players.html', context)

def player_page(request, player_id):
    player = get_object_or_404(Player, id=player_id)
    player.age = int((arrow.now() - arrow.get(player.birthDate)).days / 365.25)
    teamstrength = "even"
    scoresituation = "all"
    period = "all"
    currentSeason = Game.objects.latest("endDateTime").season
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
    pgs = PlayerGameFilterStats.objects.raw(playerqueries.playerquery, [gameids, scoresituation, teamstrength, period, player.id])
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
                if key not in ["abbreviation", "teamName", "shortName", "displayName", "fullName"]:
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
            row["toiSeconds"] = row["toi"] / row["games"]
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
    context["stats"] = stats
    if request.method == "GET" and "format" in request.GET and request.GET["format"] == "json":
        context["player"] = context["player"].__dict__
        context["player"].pop("_state", None)
        return JsonResponse(context)
    context["form"] = form
    context["statsJson"] = json.dumps(stats, cls=DjangoJSONEncoder)
    return render(request, 'players/player_page.html', context)
