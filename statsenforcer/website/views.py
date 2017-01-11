from django.shortcuts import render
from django.http import JsonResponse
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


def utc_to_local(utc_dt):
    local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
    return local_tz.normalize(local_dt) # .normalize might be unnecessary
# Create your views here.

def standings(request):
    context = {}
    max_date = SeasonStats.objects.values_list("date", "season").latest("date")
    standings = SeasonStats.objects.raw(indexqueries.standingsquery, [max_date[0], ])
    context = {
        'active_page': 'standings',
        'teams': standings
    }
    historical = SeasonStats.objects.values("team__teamName",
        "points", "date", "team__division").filter(season=max_date[1]).order_by("date")
    hstand = {}
    for h in historical:
        sdate = str(h["date"])
        teamName = h["team__teamName"]
        division = h["team__division"]
        points = h["points"]
        if division not in hstand:
            hstand[division] = {}
        if teamName not in hstand[division]:
            hstand[division][teamName] = []
        hstand[division][teamName].append({"date": sdate, "points": points})

    if request.method == "GET" and "format" in request.GET and request.GET["format"] == "json":
        context["teams"] = [x.__dict__ for x in context["teams"]]
        [x.pop("_state") for x in context["teams"]]
        return JsonResponse(context)
    else:
        context["divisions"] = json.dumps(hstand, ensure_ascii=True)
    return render(request, 'website/standings.html', context)


def index(request):
    games = Game.objects.raw(indexqueries.gamesquery, [20162017, arrow.now().datetime + datetime.timedelta(1)])
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
        elif game["endDateTime"] is not None:
            gd["finished"] = True
            gd["dateTime"] = datetime.datetime.strftime(utc_to_local(game["endDateTime"]), "%b %d, %I:%M %p %Z")
        else:
            gd["dateTime"] = datetime.datetime.strftime(utc_to_local(game["dateTime"]), "%b %d, %I:%M %p %Z")

        content["games"].append(gd)
    return JsonResponse(content)

