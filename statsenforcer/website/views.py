from django.shortcuts import render
from django.http import HttpResponse
from playbyplay.models import Game
from team.models import Team, SeasonStats
import datetime
import json
# Create your views here.

def index(request):
    games = Game.objects.filter(season=20152016).order_by('-dateTime', '-gamePk')[:30]

    #teams = Team.objects.all()
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