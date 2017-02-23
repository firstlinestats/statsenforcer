from __future__ import division
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.http import Http404, JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.serializers.json import DjangoJSONEncoder
from team.models import Team
from player.models import Player, PlayerGameFilterStats, PlayersPrecalc, GoalieGameFilterStats
from playbyplay.models import Game
from datetime import date, datetime
import json
import arrow
from playbyplay.forms import GameFilterForm, GameForm

import playerqueries

from fancystats import toi, corsi
from fancystats.goalie import adj_save_percent


def goalies(request):
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

    teamnames = {}
    teamstemp = Team.objects.all()
    for team in teamstemp:
        teamnames[team.id] = team.abbreviation
    numTeams = len(teamnames)

    stats = {}

    goalies = GoalieGameFilterStats.objects.raw(playerqueries.goaliesquery, [seasons, gameids, scoresituation, teamstrength, period])
    goalies = [g for g in goalies]

    low_shots = 0
    medium_shots = 0
    high_shots = 0

    for goalie in goalies:
        row = goalie.__dict__
        row.pop('_state')
        low_shots += row['savesLow'] + row['goalsLow']
        medium_shots += row['savesMedium'] + row['goalsMedium']
        high_shots += row['savesHigh'] + row['goalsHigh']
        if row['player_id'] not in stats:
            stats[row['player_id']] = row
            stats[row['player_id']]['games'] = 1
            stats[row['player_id']]['game_ids'] = [row['game_id'], ]
        else:
            player_id = row['player_id']
            stats[player_id]['games'] += 1
            stats[player_id]['game_ids'].append(row['game_id'])
            for key in row:
                if key not in ['player_id', 'game_id', 'team_id', 'season', 'fullName']:
                    val = row[key]
                    stats[player_id][key] += val

    for pid in stats:
        goalie = stats[pid]
        goalie['saves'] = goalie['savesLow'] + goalie['savesMedium'] + goalie['savesHigh'] + goalie['savesUnknown']
        goalie['goals'] = goalie['goalsLow'] + goalie['goalsMedium'] + goalie['goalsHigh'] + goalie['goalsUnknown']
        goalie['save_percent'] = '%.1f' % corsi.corsi_percent(goalie['saves'], goalie['goals'])
        goalie['low_save_percent'] = '%.1f' % corsi.corsi_percent(goalie['savesLow'], goalie['goalsLow'])
        goalie['medium_save_percent'] = '%.1f' % corsi.corsi_percent(goalie['savesMedium'], goalie['goalsMedium'])
        goalie['high_save_percent'] = '%.1f' % corsi.corsi_percent(goalie['savesHigh'], goalie['goalsHigh'])
        goalie['unknown_save_percent'] = '%.1f' % corsi.corsi_percent(goalie['savesUnknown'], goalie['goalsUnknown'])
        goalie['adj_save_percent'] = adj_save_percent(goalie['savesLow'],
                                                      goalie['savesMedium'],
                                                      goalie['savesHigh'],
                                                      goalie['goalsLow'],
                                                      goalie['goalsMedium'],
                                                      goalie['goalsHigh'],
                                                      low_shots,
                                                      medium_shots,
                                                      high_shots)

    context = {}
    context['stats'] = stats.values()

    if request.method == "GET" and "format" in request.GET and request.GET["format"] == "json":
        return JsonResponse(context)

    context['form'] = form

    return render(request, 'players/goalies.html', context)



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
        if endDate is None:
            endDate = arrow.utcnow().datetime
    if endDate is not None:
        gameids = gameids.filter(dateTime__date__lte=endDate)
    if len(venues) > 0:
        gameids = gameids.filter(venue__in=venues)
    if len(teams) > 0:
        gameids = gameids.filter(Q(homeTeam__in=cd['teams']) | Q(awayTeam__in=cd['teams']))
    gameids = [x for x in gameids]

    teamnames = {}
    teamstemp = Team.objects.all()
    for team in teamstemp:
        teamnames[team.id] = team.abbreviation
    numTeams = len(teamnames)
    if not teams:
        teams = Team.objects.all()

    stats = []

    if (not startDate and not endDate and (not teams or len(teams) == numTeams) and not venues):
        players = PlayersPrecalc.objects.raw(playerqueries.precalc_players, [seasons, scoresituation, teamstrength, period])
        players = [p for p in players]
        for p in players:
            row = p.__dict__
            row.pop("_state")
            toiSeconds = row["toi"]
            row["toi"] = toi.format_minutes(row["toi"] / row["games"])
            row["player_id"] = row["player"]
            row['ca60'] = '%.1f' % (corsi.corsi_for_60(toiSeconds, row["corsiAgainst"]) * 60)
            row['fa60'] = '%.1f' % (corsi.corsi_for_60(toiSeconds, row["fenwickAgainst"]) * 60)
            row['csh'] = '%.1f' % corsi.corsi_percent(row['goalsFor'], row['corsiFor'])
            row['csa'] = '%.1f' % (100 - corsi.corsi_percent(row['goalsAgainst'], row['corsiAgainst']))
            row['fsh'] = '%.1f' % corsi.corsi_percent(row['goalsFor'], row['fenwickFor'])
            row['fsa'] = '%.1f' % (100 - corsi.corsi_percent(row['goalsAgainst'], row['fenwickAgainst']))
            stats.append(row)

    elif (startDate is not None and endDate is not None):
        players = PlayerGameFilterStats.objects.raw(playerqueries.playersquery_historical_daterange, [startDate, endDate, scoresituation, teamstrength, period])
        players = [p for p in players]
        for playerid in players:
            row = playerid.__dict__
            row.pop("_state")
            toiSeconds = row["toi"]
            row["team"] = teamnames[row["team_id"]]
            row["toi"] = toi.format_minutes(row["toi"] / row["games"])
            row["fo"] = '%.1f' % corsi.corsi_percent(row["fo_w"], row["fo_l"])
            row["sf"] = '%.1f' % corsi.corsi_percent(row["shotsFor"], row["shotsAgainst"])
            row["msf"] = '%.1f' % corsi.corsi_percent(row["missedShotsFor"],
                row["missedShotsAgainst"])
            row["bsf"] = '%.1f' % corsi.corsi_percent(row["blockedShotsFor"],
                row["blockedShotsAgainst"])
            row["gf"] = '%.1f' % corsi.corsi_percent(row["goalsFor"], row["goalsAgainst"])
            row["cf"] = '%.1f' % corsi.corsi_percent(row["corsiFor"], row["corsiAgainst"])
            row["ff"] = '%.1f' % corsi.corsi_percent(row["fenwickFor"], row["fenwickAgainst"])
            row["hit"] = '%.1f' % corsi.corsi_percent(row["hitFor"], row["hitAgainst"])
            row["pn"] = '%.1f' % corsi.corsi_percent(row["penaltyFor"], row["penaltyAgainst"])
            row["scf"] = '%.1f' % corsi.corsi_percent(row["scoringChancesFor"], row["scoringChancesAgainst"])
            row["hscf"] = '%.1f' % corsi.corsi_percent(row["highDangerScoringChancesFor"], row["highDangerScoringChancesAgainst"])
            row['gf60'] = '%.1f' % (corsi.corsi_for_60(toiSeconds, row["goalsFor"]) * 60)
            row['a60'] = '%.1f' % (corsi.corsi_for_60(toiSeconds, row["assists1"] + row["assists2"]) * 60)
            row['a160'] = '%.1f' % (corsi.corsi_for_60(toiSeconds, row["assists1"]) * 60)
            row['p60'] = '%.1f' % (corsi.corsi_for_60(toiSeconds, row["points"]) * 60)
            row['scf60'] = '%.1f' % (corsi.corsi_for_60(toiSeconds, row["scoringChancesFor"]) * 60)
            row['cf60'] = '%.1f' % (corsi.corsi_for_60(toiSeconds, row["corsiFor"]) * 60)
            row['ca60'] = '%.1f' % (corsi.corsi_for_60(toiSeconds, row["corsiAgainst"]) * 60)
            row['ff60'] = '%.1f' % (corsi.corsi_for_60(toiSeconds, row["fenwickFor"]) * 60)
            row['fa60'] = '%.1f' % (corsi.corsi_for_60(toiSeconds, row["fenwickAgainst"]) * 60)
            row['hscf60'] = '%.1f' % (corsi.corsi_for_60(toiSeconds, row["highDangerScoringChancesFor"]) * 60)
            row['csh'] = '%.1f' % corsi.corsi_percent(row['goalsFor'], row['corsiFor'])
            row['csa'] = '%.1f' % (100 - corsi.corsi_percent(row['goalsAgainst'], row['corsiAgainst']))
            row['fsh'] = '%.1f' % corsi.corsi_percent(row['goalsFor'], row['fenwickFor'])
            row['fsa'] = '%.1f' % (100 - corsi.corsi_percent(row['goalsAgainst'], row['fenwickAgainst']))
            if row["neutralZoneStarts"] is not None:
                row["zso"] = '%.1f' % corsi.corsi_percent(row["offensiveZoneStarts"], row["neutralZoneStarts"] + row["defensiveZoneStarts"])
            else:
                row["zso"] = "0.0"
            stats.append(row)
    else:
        playergames = PlayerGameFilterStats.objects.raw(playerqueries.playersquery, [seasons, gameids, scoresituation, teamstrength, period, [x.id for x in teams]])
        players = {}
        for player in playergames:
            player = player.__dict__
            if player["player_id"] not in players:
                player.pop("_state")
                players[player["player_id"]] = player
                players[player["player_id"]]["games"] = 1
            else:
                for key in player:
                    if key not in ["_state", "id", "player_id", "game_id", "team_id", "season", "abbreviation", "shortName", "teamName", "fullName"]:
                        players[player["player_id"]][key] += player[key]
                players[player["player_id"]]["games"] += 1

        for playerid in players:
            row = players[playerid]
            toiSeconds = row["toi"]
            row["team"] = teamnames[row["team_id"]]
            row["toi"] = toi.format_minutes(row["toi"] / row["games"])
            row["fo"] = '%.1f' % corsi.corsi_percent(row["fo_w"], row["fo_l"])
            row["sf"] = '%.1f' % corsi.corsi_percent(row["shotsFor"], row["shotsAgainst"])
            row["msf"] = '%.1f' % corsi.corsi_percent(row["missedShotsFor"],
                row["missedShotsAgainst"])
            row["bsf"] = '%.1f' % corsi.corsi_percent(row["blockedShotsFor"],
                row["blockedShotsAgainst"])
            row["gf"] = '%.1f' % corsi.corsi_percent(row["goalsFor"], row["goalsAgainst"])
            row["cf"] = '%.1f' % corsi.corsi_percent(row["corsiFor"], row["corsiAgainst"])
            row["ff"] = '%.1f' % corsi.corsi_percent(row["fenwickFor"], row["fenwickAgainst"])
            row["hit"] = '%.1f' % corsi.corsi_percent(row["hitFor"], row["hitAgainst"])
            row["pn"] = '%.1f' % corsi.corsi_percent(row["penaltyFor"], row["penaltyAgainst"])
            row["scf"] = '%.1f' % corsi.corsi_percent(row["scoringChancesFor"], row["scoringChancesAgainst"])
            row["hscf"] = '%.1f' % corsi.corsi_percent(row["highDangerScoringChancesFor"], row["highDangerScoringChancesAgainst"])
            row['gf60'] = '%.1f' % (corsi.corsi_for_60(toiSeconds, row["goalsFor"]) * 60)
            row['a60'] = '%.1f' % (corsi.corsi_for_60(toiSeconds, row["assists1"] + row["assists2"]) * 60)
            row['a160'] = '%.1f' % (corsi.corsi_for_60(toiSeconds, row["assists1"]) * 60)
            row['p60'] = '%.1f' % (corsi.corsi_for_60(toiSeconds, row["points"]) * 60)
            row['scf60'] = '%.1f' % (corsi.corsi_for_60(toiSeconds, row["scoringChancesFor"]) * 60)
            row['cf60'] = '%.1f' % (corsi.corsi_for_60(toiSeconds, row["corsiFor"]) * 60)
            row['ca60'] = '%.1f' % (corsi.corsi_for_60(toiSeconds, row["corsiAgainst"]) * 60)
            row['ff60'] = '%.1f' % (corsi.corsi_for_60(toiSeconds, row["fenwickFor"]) * 60)
            row['fa60'] = '%.1f' % (corsi.corsi_for_60(toiSeconds, row["fenwickAgainst"]) * 60)
            row['hscf60'] = '%.1f' % (corsi.corsi_for_60(toiSeconds, row["highDangerScoringChancesFor"]) * 60)
            row['csh'] = '%.1f' % corsi.corsi_percent(row['goalsFor'], row['corsiFor'])
            row['csa'] = '%.1f' % (100 - corsi.corsi_percent(row['goalsAgainst'], row['corsiAgainst']))
            row['fsh'] = '%.1f' % corsi.corsi_percent(row['goalsFor'], row['fenwickFor'])
            row['fsa'] = '%.1f' % (100 - corsi.corsi_percent(row['goalsAgainst'], row['fenwickAgainst']))
            if row["neutralZoneStarts"] is not None:
                row["zso"] = '%.1f' % corsi.corsi_percent(row["offensiveZoneStarts"], row["neutralZoneStarts"] + row["defensiveZoneStarts"])
            else:
                row["zso"] = "0.0"
            stats.append(row)

    context = {}
    context["stats"] = stats
    if request.method == "GET" and "format" in request.GET and request.GET["format"] == "json":
        pgidlist = PlayerGameFilterStats.objects.raw(playerqueries.playeridquery, [gameids, scoresituation, teamstrength, period])
        pgids = {}
        for pgid in pgidlist:
            if pgid.player_id not in pgids:
                pgids[pgid.player_id] = {}
            season = int(str(pgid.game_id)[:4] + str(int(str(pgid.game_id)[:4]) + 1))
            if season not in pgids[pgid.player_id]:
                pgids[pgid.player_id][season] = []
            pgids[pgid.player_id][season].append(pgid.game_id)
        for player in stats:
            season = player['season']
            playerid = player['player_id']
            if playerid in pgids and season in pgids[playerid]:
                player['game_ids'] = pgids[playerid][season]
            else:
                player['game_ids'] = []
        return JsonResponse(context)
    context["form"] = form
    context["statsJson"] = json.dumps(stats, cls=DjangoJSONEncoder)
    return render(request, 'players/players.html', context)


def goalie_page(request, player_id):
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
    pgs = GoalieGameFilterStats.objects.raw(playerqueries.goaliequery, [gameids, scoresituation, teamstrength, period, player.id])
    sdata = GoalieGameFilterStats.objects.raw(playerqueries.goalieshotsquery, [gameids, scoresituation, teamstrength, period])
    low_shots = 0
    medium_shots = 0
    high_shots = 0
    for s in sdata:
        low_shots += s.savesLow + s.goalsLow
        medium_shots += s.savesMedium + s.goalsMedium
        high_shots += s.savesHigh + s.goalsHigh
    stats = {}
    for row in pgs:
        season = row.season
        playerid = player.id
        if playerid not in stats:
            stats[playerid] = {}
        if season not in stats[playerid]:
            stats[playerid][season] = row.__dict__
            stats[playerid][season]["games"] = 1
            stats[playerid][season]['game_ids'] = [row.__dict__['game_id'], ]
            stats[playerid][season].pop("_state", None)
            stats[playerid][season].pop("game_id", None)
            stats[playerid][season].pop("period", None)
            stats[playerid][season].pop("teamstrength", None)
            stats[playerid][season].pop("scoresituation", None)
            stats[playerid][season].pop("player_id", None)
        else:
            stats[playerid][season]["games"] += 1
            stats[playerid][season]['game_ids'].append(row.__dict__['game_id'])
            for key in stats[playerid][season]:
                if key not in ["abbreviation", "teamName", "shortName", "displayName", "fullName", "season"]:
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
            goalie = stats[playerid][season]
            goalie["toiSeconds"] = goalie["toi"] / goalie["games"]
            goalie["toi"] = toi.format_minutes(goalie["toi"] / goalie["games"])
            goalie['saves'] = goalie['savesLow'] + goalie['savesMedium'] + goalie['savesHigh'] + goalie['savesUnknown']
            goalie['goals'] = goalie['goalsLow'] + goalie['goalsMedium'] + goalie['goalsHigh'] + goalie['goalsUnknown']
            goalie['save_percent'] = '%.1f' % corsi.corsi_percent(goalie['saves'], goalie['goals'])
            goalie['low_save_percent'] = '%.1f' % corsi.corsi_percent(goalie['savesLow'], goalie['goalsLow'])
            goalie['medium_save_percent'] = '%.1f' % corsi.corsi_percent(goalie['savesMedium'], goalie['goalsMedium'])
            goalie['high_save_percent'] = '%.1f' % corsi.corsi_percent(goalie['savesHigh'], goalie['goalsHigh'])
            goalie['unknown_save_percent'] = '%.1f' % corsi.corsi_percent(goalie['savesUnknown'], goalie['goalsUnknown'])
            goalie['adj_save_percent'] = adj_save_percent(goalie['savesLow'],
                                                          goalie['savesMedium'],
                                                          goalie['savesHigh'],
                                                          goalie['goalsLow'],
                                                          goalie['goalsMedium'],
                                                          goalie['goalsHigh'],
                                                          low_shots,
                                                          medium_shots,
                                                          high_shots)

    context = {}
    context["player"] = player
    context["stats"] = stats
    if request.method == "GET" and "format" in request.GET and request.GET["format"] == "json":
        context["player"] = context["player"].__dict__
        context["player"].pop("_state", None)
        return JsonResponse(context)
    context["form"] = form
    context["statsJson"] = json.dumps(stats, cls=DjangoJSONEncoder)
    return render(request, 'players/goalie_page.html', context)


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
            stats[playerid][season]['game_ids'] = [row.__dict__['game_id'], ]
            stats[playerid][season].pop("_state", None)
            stats[playerid][season].pop("game_id", None)
            stats[playerid][season].pop("period", None)
            stats[playerid][season].pop("teamstrength", None)
            stats[playerid][season].pop("scoresituation", None)
            stats[playerid][season].pop("player_id", None)
        else:
            stats[playerid][season]["games"] += 1
            stats[playerid][season]['game_ids'].append(row.__dict__['game_id'])
            for key in stats[playerid][season]:
                if key not in ["season", "abbreviation", "teamName", "shortName", "displayName", "fullName"]:
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
            toiSeconds = row["toi"]
            row["toi"] = toi.format_minutes(row["toi"] / row["games"])
            row["fo"] = '%.1f' % corsi.corsi_percent(row["fo_w"], row["fo_l"])
            row["sf"] = '%.1f' % corsi.corsi_percent(row["shotsFor"], row["shotsAgainst"])
            row["msf"] = '%.1f' % corsi.corsi_percent(row["missedShotsFor"],
                row["missedShotsAgainst"])
            row["bsf"] = '%.1f' % corsi.corsi_percent(row["blockedShotsFor"],
                row["blockedShotsAgainst"])
            row["gf"] = '%.1f' % corsi.corsi_percent(row["goalsFor"], row["goalsAgainst"])
            row["cf"] = '%.1f' % corsi.corsi_percent(row["corsiFor"], row["corsiAgainst"])
            row["ff"] = '%.1f' % corsi.corsi_percent(row["fenwickFor"], row["fenwickAgainst"])
            row["hit"] = '%.1f' % corsi.corsi_percent(row["hitFor"], row["hitAgainst"])
            row["pn"] = '%.1f' % corsi.corsi_percent(row["penaltyFor"], row["penaltyAgainst"])
            row["scf"] = '%.1f' % corsi.corsi_percent(row["scoringChancesFor"], row["scoringChancesAgainst"])
            row["hscf"] = '%.1f' % corsi.corsi_percent(row["highDangerScoringChancesFor"], row["highDangerScoringChancesAgainst"])
            row['gf60'] = '%.1f' % (corsi.corsi_for_60(toiSeconds, row["goalsFor"]) * 60)
            row['a60'] = '%.1f' % (corsi.corsi_for_60(toiSeconds, row["assists1"] + row["assists2"]) * 60)
            row['a160'] = '%.1f' % (corsi.corsi_for_60(toiSeconds, row["assists1"]) * 60)
            row['p60'] = '%.1f' % (corsi.corsi_for_60(toiSeconds, row["points"]) * 60)
            row['scf60'] = '%.1f' % (corsi.corsi_for_60(toiSeconds, row["scoringChancesFor"]) * 60)
            row['cf60'] = '%.1f' % (corsi.corsi_for_60(toiSeconds, row["corsiFor"]) * 60)
            row['ca60'] = '%.1f' % (corsi.corsi_for_60(toiSeconds, row["corsiAgainst"]) * 60)
            row['ff60'] = '%.1f' % (corsi.corsi_for_60(toiSeconds, row["fenwickFor"]) * 60)
            row['fa60'] = '%.1f' % (corsi.corsi_for_60(toiSeconds, row["fenwickAgainst"]) * 60)
            row['hscf60'] = '%.1f' % (corsi.corsi_for_60(toiSeconds, row["highDangerScoringChancesFor"]) * 60)
            row['csh'] = '%.1f' % corsi.corsi_percent(row['goalsFor'], row['corsiFor'])
            row['csa'] = '%.1f' % (100 - corsi.corsi_percent(row['goalsAgainst'], row['corsiAgainst']))
            row['fsh'] = '%.1f' % corsi.corsi_percent(row['goalsFor'], row['fenwickFor'])
            row['fsa'] = '%.1f' % (100 - corsi.corsi_percent(row['goalsAgainst'], row['fenwickAgainst']))
            if row["neutralZoneStarts"] is not None:
                row["zso"] = '%.1f' % corsi.corsi_percent(row["offensiveZoneStarts"], row["defensiveZoneStarts"])
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
