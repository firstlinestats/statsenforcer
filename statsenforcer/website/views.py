from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.core.serializers.json import DjangoJSONEncoder

from playbyplay.templatetags.pbp_extras import get_period
from playbyplay.models import Game, PlayByPlay
from team.models import Team, SeasonStats
from website.models import GlossaryTerm

import datetime
import json
import pytz
import arrow

from fancystats.constants import gameStates

import indexqueries

local_tz = pytz.timezone('US/Eastern')


def rink(request):
    image_data = open("static/svg/rink.png", "rb").read()
    return HttpResponse(image_data, content_type="image/png")


def utc_to_local(utc_dt):
    local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
    return local_tz.normalize(local_dt) # .normalize might be unnecessary


def configure_standing(teamPlace, antiPlace, teamStandings, game):
    """
        ("PNow", "Points, Under Current System"),
        ("P3", "Points, 3-2-1-0 System"),
        ("PTie", "Points, Tie After Overtime Ends"),
        ("PNL", "Points, No Tie or Loser Points")
    """
    teamName = game["{}TeamName".format(teamPlace)]
    teamAbbreviation = game["{}Abbreviation".format(teamPlace)]
    teamDivision = game["{}Division".format(teamPlace)]
    team_id = game["{}Team_id".format(teamPlace)]
    teamScore = game["{}Score".format(teamPlace)]
    otherScore = game["{}Score".format(antiPlace)]
    sdate = game["startDate"].strftime("%Y-%m-%d")
    OT = game["gameOT"] == 1
    shootout = game["gameShootout"] == 1
    if teamDivision not in teamStandings:
        teamStandings[teamDivision] = {}
    if teamName not in teamStandings[teamDivision]:
        teamStandings[teamDivision][teamName] = []
        points = 0
        points3 = 0
        pointstie = 0
        pointsnl = 0
        gamesPlayed = 1
        wins = 0
        losses = 0
        goalsFor = 0
        goalsAgainst = 0
        streakCode = "W0"
    else:
        points = teamStandings[teamDivision][teamName][-1]["points"]
        points3 = teamStandings[teamDivision][teamName][-1]["points3"]
        pointstie = teamStandings[teamDivision][teamName][-1]["pointstie"]
        pointsnl = teamStandings[teamDivision][teamName][-1]["pointsnl"]
        gamesPlayed = teamStandings[teamDivision][teamName][-1]["gamesPlayed"] + 1
        wins = teamStandings[teamDivision][teamName][-1]["wins"]
        losses = teamStandings[teamDivision][teamName][-1]["losses"]
        goalsFor = teamStandings[teamDivision][teamName][-1]["goalsFor"]
        goalsAgainst = teamStandings[teamDivision][teamName][-1]["goalsAgainst"]
        streakCode = teamStandings[teamDivision][teamName][-1]["streakCode"]
    winner = teamScore > otherScore
    goalsFor += teamScore
    goalsAgainst += otherScore
    if winner:
        if "W" in streakCode:
            streakCode = "W{}".format(int(streakCode.replace("W", "")) + 1)
        else:
            streakCode = "W1"
        pointsnl += 1
        wins += 1
        points += 2
        if OT:
            points3 += 2
            if not shootout:
                pointstie += 2
            else:
                goalsFor -= 1
        else:
            points3 += 3
            pointstie += 2
    else:
        if "L" in streakCode:
            streakCode = "L{}".format(int(streakCode.replace("L", "")) + 1)
        else:
            streakCode = "L1"
        losses += 1
        if OT:
            points += 1
            points3 += 1
            if not shootout:
                pointstie += 1
            else:
                goalsAgainst -= 1
    if shootout:
        pointstie += 1

    teamStandings[teamDivision][teamName].append({"dateString": sdate,
                                                  "gamesPlayed": gamesPlayed,
                                                  "points": points,
                                                  "points3": points3,
                                                  "pointstie": pointstie,
                                                  "pointsnl": pointsnl,
                                                  "wins": wins,
                                                  "losses": losses,
                                                  "goalsFor": goalsFor,
                                                  "goalsAgainst": goalsAgainst,
                                                  "abbreviation": teamAbbreviation,
                                                  "streakCode": streakCode})


def standings(request):
    context = {}

    currentSeason = Game.objects.latest("endDateTime").season
    games = Game.objects.raw(indexqueries.standingsquery, [currentSeason, ])
    teamStandings = {}
    for game in games:
        game = game.__dict__
        configure_standing("home", "away", teamStandings, game)
        configure_standing("away", "home", teamStandings, game)

    teams = {}
    for div in teamStandings:
        for team in teamStandings[div]:
            last = teamStandings[div][team][-1]
            last["team_division"] = div
            teams[team] = last

    context["divisions"] = json.dumps(teamStandings, ensure_ascii=True)
    context["teams"] = teams
    if request.method == "GET" and "format" in request.GET and request.GET["format"] == "json":
        return JsonResponse(context)
    return render(request, 'website/standings.html', context)


def index(request):
    currentSeason = Game.objects.latest("endDateTime").season
    games = Game.objects.raw(indexqueries.gamesquery, [currentSeason, arrow.now().datetime + datetime.timedelta(1)])
    context = {
        'games': games,
    }

    if request.method == "GET" and "format" in request.GET and request.GET["format"] == "json":
        context["games"] = [x.__dict__ for x in context["games"]]
        [x.pop("_state") for x in context["games"]]
        return JsonResponse(context)
    return render(request, 'website/index.html', context)


def about(request):
    return render(request, 'website/about.html')


def glossary(request):
    terms = GlossaryTerm.objects.all()
    if request.method == "GET" and "format" in request.GET and request.GET["format"] == "json":
        terms = [x.__dict__ for x in terms]
        [x.pop("_state", None) for x in terms]
        return JsonResponse(terms, safe=False)
    return render(request, 'website/glossary.html', {'terms': terms})


def games(request, gamedate):
    content = {"games": []}
    dateurlformat = "YYYY-MM-DD"
    dateformat = "%b %d"
    if gamedate == "today":
        gamedate = arrow.now().datetime
    else:
        return JsonResponse({'status': 'false', 'message': 'There was an issue with the provided date format, currently only \'today\' is accepted'}, status=400)
    games = Game.objects.values("gamePk", "homeTeam__abbreviation", "awayTeam__abbreviation", "homeScore", "awayScore", "dateTime", "endDateTime", "gameState").filter(dateTime__gte=gamedate - datetime.timedelta(hours=24), dateTime__lte=gamedate + datetime.timedelta(hours=12)).order_by("endDateTime")
    content["date"] = datetime.datetime.strftime(gamedate, dateformat)
    content["yesterday"] = datetime.datetime.strftime(gamedate - datetime.timedelta(hours=24), dateurlformat)
    content["tomorrow"] = datetime.datetime.strftime(gamedate + datetime.timedelta(hours=24), dateurlformat)
    for game in games:
        gd = {}
        gd["gameId"] = game["gamePk"]
        gd["homeScore"] = game["homeScore"]
        gd["awayScore"] = game["awayScore"]
        gd["homeTeamAbbreviation"] = game["homeTeam__abbreviation"]
        gd["awayTeamAbbreviation"] = game["awayTeam__abbreviation"]
        gd["live"] = False
        gd["finished"] = False
        if game["gameState"] in ["3", "4"]:
            gd["live"] = True
            lastPlay = PlayByPlay.objects.filter(gamePk_id=game["gamePk"]).latest("eventIdx")
            pt = str(lastPlay.periodTime)[:-3].split(":")
            minutes = 20 - int(pt[0])
            seconds = 60 - int(pt[1])
            if seconds == 60:
                seconds = 0
            else:
                minutes -= 1
            minutes = str(minutes)
            seconds = str(seconds)
            if len(minutes) == 1:
                minutes = "0{}".format(minutes)
            if len(seconds) == 1:
                seconds = "0{}".format(seconds)
            periodTimeString = "{}:{}".format(minutes, seconds)
            periodVal = get_period(lastPlay.period)
            if periodTimeString != "00:00":
                gd["dateTime"] = "{} {}".format(periodVal, periodTimeString)
            else:
                gd["dateTime"] = "End of {}".format(periodVal)
        elif game["gameState"] in ["5", "6", "7"]:
            gd["finished"] = True
            gd["dateTime"] = datetime.datetime.strftime(utc_to_local(game["dateTime"]), "%b %d, %I:%M %p %Z")
        else:
            gd["dateTime"] = datetime.datetime.strftime(utc_to_local(game["dateTime"]), "%b %d, %I:%M %p %Z")

        content["games"].append(gd)
    return JsonResponse(content)

