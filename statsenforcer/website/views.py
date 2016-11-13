from django.shortcuts import render
from django.http import JsonResponse
from playbyplay.models import Game, PlayByPlay
from team.models import Team, SeasonStats
import datetime
import json
from playbyplay.templatetags.pbp_extras import get_period
# Create your views here.

def index(request):
    games = Game.objects.filter(season=20162017, dateTime__lte=datetime.date.today() + datetime.timedelta(1)).order_by('-dateTime', '-gamePk')[:30]

    teamdata = {}
    currentSeason = games[0].season
    max_date = SeasonStats.objects.latest("date")
    standings = SeasonStats.objects.filter(date=max_date.date).order_by("-points")
    teamdata = sorted(teamdata.items(), key=lambda k: k[1]["p"])
    context = {
        'active_page': 'index',
        'games': games,
        'teams': standings
    }

    return render(request, 'website/index.html', context)


def games(request, gamedate):
    content = {"games": []}
    dateurlformat = "%Y-%m-%d"
    dateformat = "%b %d"
    try:
        if gamedate == "today":
            gamedate = datetime.datetime.today()
            print gamedate
        else:
            gamedate = datetime.datetime.strptime(gamedate, dateurlformat)
        gameenddate = gamedate - datetime.timedelta(hours=36)
    except Exception as e:
        print e
        return JsonResponse({'status': 'false', 'message': 'There was an issue with the provided date format'}, status=400)
    games = Game.objects.filter(gameState__in=["3", "4"])
    content["date"] = datetime.datetime.strftime(gamedate, dateformat)
    content["yesterday"] = datetime.datetime.strftime(gamedate - datetime.timedelta(hours=24), dateurlformat)
    content["tomorrow"] = datetime.datetime.strftime(gamedate + datetime.timedelta(hours=24), dateurlformat)
    for game in games:
        gd = {}
        gd["gameId"] = game.gamePk
        gd["homeTeam"] = game.homeTeam.teamName
        gd["awayTeam"] = game.awayTeam.teamName
        gd["homeScore"] = game.homeScore
        gd["awayScore"] = game.awayScore
        gd["homeTeamAbbreviation"] = game.homeTeam.abbreviation
        gd["awayTeamAbbreviation"] = game.awayTeam.abbreviation
        lastPlay = PlayByPlay.objects.filter(gamePk=game).latest("eventIdx")
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
        gd["dateTime"] = "{} {}".format(periodVal, periodTimeString)

        content["games"].append(gd)
    return JsonResponse(content)
