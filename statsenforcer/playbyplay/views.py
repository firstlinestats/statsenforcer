from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.core.serializers.json import DjangoJSONEncoder
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

import pytz
import json

import fancystats

from . import models
from . import forms
from team import models as tmodels
from playbyplay.models import Game

# Create your views here.
def game(request, game_pk):
    context = {}
    context["game"] = get_object_or_404(models.Game, gamePk=game_pk)
    context["form"] = forms.GameForm()
    teamStrengths = "all"
    scoreSituation = "all"
    hsc = 0
    asc = 0
    period = "all"
    if request.method == "GET":
        context["form"] = forms.GameForm(request.GET)
        if context["form"].is_valid():
            cd = context["form"].cleaned_data
            teamStrengths = cd["teamstrengths"]
            scoreSituation = cd["scoresituation"]
            period = cd["period"]
    context["game"].dateTime = context["game"].dateTime.astimezone(pytz.timezone('US/Eastern'))
    try:
        context["period"] = models.GamePeriod.objects.filter(game_id=game_pk).latest("startTime")
    except:
        context["period"] = None
    if context["period"] is not None:
        context["playbyplay"] = models.PlayByPlay.objects.filter(gamePk_id=game_pk).order_by("eventIdx")
        context["playbyplay"] = [x.__dict__ for x in context["playbyplay"]]
        media = models.PlayMedia.objects.values("title", "blurb", "description", "duration", "image", "play", "external_id").filter(game_id=game_pk)
        context["playmedia"] = {}
        year, game = game_pk[:4], game_pk[5:]
        for m in media:
            mdata = m
            mdata["url"] = "https://www.nhl.com/video/c-{}".format(m["external_id"])
            mdata["preview"] = "http://static.firstlinestats.com.s3.amazonaws.com/preview/{}/{}/{}.jpeg".format(year, game, m["external_id"])
            context["playmedia"][m["play"]] = mdata

        playerteams = models.PlayerGameStats.objects.values("team__abbreviation", "team_id", "player_id", "player__fullName", "player__primaryPositionCode").filter(game_id=game_pk)
        p2t = {}
        for p in playerteams:
            p2t[p["player_id"]] = [p["team__abbreviation"], p["team_id"], 0, p["player__fullName"], p["player__primaryPositionCode"]]
        goalieteams = models.GoalieGameStats.objects.values("team__abbreviation", "team_id", "player_id", "player__fullName", "player__primaryPositionCode").filter(game_id=game_pk)
        for p in goalieteams:
            p2t[p["player_id"]] = [p["team__abbreviation"], p["team_id"], 1, p["player__fullName"], p["player__primaryPositionCode"]]

        pip_data = models.PlayerInPlay.objects.values("player_type", "play_id", "player__fullName", "player__primaryPositionCode", "player_id").filter(play_id__in=[x["id"] for x in context["playbyplay"]])
        pipdict = {}
        for poi in pip_data:
            if poi["play_id"] not in pipdict:
                pipdict[poi["play_id"]] = []
            if poi["player_id"] in p2t:
                poi["player__fullNameTeam"] = poi["player__fullName"] + " (" + p2t[poi["player_id"]][0] + ")"
            pipdict[poi["play_id"]].append(poi)

        poi_data = models.PlayerOnIce.objects.values("player_id", "play_id", "player__lastName", "player__primaryPositionCode").filter(play_id__in=[x["id"] for x in context["playbyplay"]])
        poidict = {}
        for poi in poi_data:
            poi["team_id"] = p2t[poi["player_id"]][1]
            if poi["play_id"] not in poidict:
                poidict[poi["play_id"]] = []
            poidict[poi["play_id"]].append(poi)
        order = ["L", "C", "R", "D", "G"]
        for play in poidict:
            poidict[play] = sorted(poidict[play], key=lambda x: order.index(x["player__primaryPositionCode"]))

        pt = str(context["playbyplay"][-1]["periodTime"])[:-3].split(":")
        if context["period"].period < 4 or context["game"].gameType == "P":
            minutes = 20 - int(pt[0])
        else:
            minutes = 5 - int(pt[0])
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

        context["periodTimeString"] = periodTimeString
        for play in context["playbyplay"]:
            play["periodTimeString"] = str(play["periodTime"])[:-3]
            if play["id"] in pipdict:
                play["players"] = pipdict[play["id"]]
            else:
                play["players"] = []
            if play["id"] in poidict:
                play["onice"] = poidict[play["id"]]
            else:
                play["onice"] = []
        context["teamstats"] = fancystats.team.get_stats(
            context["playbyplay"],
            context["game"].homeTeam.id,
            context["game"].awayTeam.id,
            p2t,
            teamStrengths=teamStrengths,
            scoreSituation=scoreSituation,
            period=period)
        for ts in context["teamstats"]:
            team = get_object_or_404(tmodels.Team, id=ts)
            context["teamstats"][ts]["team"] = team.abbreviation

        context["playerstats"] = fancystats.player.get_stats(
            context["playbyplay"],
            context["game"].homeTeam.id,
            context["game"].awayTeam.id,
            p2t,
            teamStrengths=teamStrengths,
            scoreSituation=scoreSituation,
            period=period)

        context["playersjson"] = json.dumps(context["playerstats"])

        context["goaliestats"] = fancystats.player.get_goalie_stats(
            context["playbyplay"],
            context["game"].homeTeam.id,
            context["game"].awayTeam.id,
            p2t,
            teamStrengths=teamStrengths,
            scoreSituation=scoreSituation,
            period=period)

        shotData = {
            "home" : [],
            "away" : []
        }
        for play in context["playbyplay"]:
            if play["playType"] in ["SHOT", "GOAL", "MISSED_SHOT", "BLOCKED_SHOT"]:
                scoringChance = fancystats.shot.scoring_chance_standard(play, None, None)
                danger = scoringChance[0]
                sc = scoringChance[1]
                team = play["team_id"]
                play_type = play["playType"]
                homeinclude, awayinclude = fancystats.team.check_play(play, teamStrengths, scoreSituation, period, hsc, asc, context["game"].homeTeam.id, context["game"].awayTeam.id, p2t)
                if team == context["game"].homeTeam.id and homeinclude:
                    xcoord = play["xcoord"]
                    ycoord = play["ycoord"]
                    if xcoord < 0 and xcoord is not None:
                        xcoord = abs(xcoord)
                        ycoord = ycoord
                    shotData["home"].append({"x": xcoord,
                        "y": ycoord, "type": play_type, "danger": danger, "description": play["playDescription"],
                        "scoring_chance": sc, "time": str(play["periodTime"])[:-3], "period": play["period"]})
                elif team == context["game"].awayTeam.id and awayinclude:
                    xcoord = play["xcoord"]
                    ycoord = play["ycoord"]
                    if xcoord > 0:
                        xcoord = -xcoord
                        ycoord = -ycoord
                    shotData["away"].append({"x": xcoord,
                        "y": ycoord, "type": play_type, "danger": danger, "description": play["playDescription"],
                        "scoring_chance": sc, "time": str(play["periodTime"])[:-3], "period": play["period"]})
        context["shotdatajson"] = json.dumps(shotData, cls=DjangoJSONEncoder)


        context["teamstats"] = context["teamstats"].values()
    return render(request, 'games/game.html', context)


def games(request):
    form = forms.GamesForm()
    cd = {'startDate': None, 'endDate': None, 'gameTypes': [],
        'venues': [], 'teams': [], 'seasons': []}
    if request.method == 'GET':
        formcheck = False
        if len(request.GET) > 1:
            if "page" not in request.GET:
                formcheck = True
            else:
                if len(request.GET) > 2:
                    formcheck = True
        if formcheck:
            form = forms.GamesForm(request.GET)
            if form.is_valid():
                cd = form.cleaned_data
            else:
                form = forms.GamesForm()

    games = Game.objects.values("gamePk", "dateTime", "homeTeam__abbreviation", "gameType",
        "homeTeam__teamName", "awayTeam__abbreviation", "awayTeam__teamName", "homeScore",
        "awayScore", "homeShots", "awayShots", "awayBlocked", "homeMissed", "homeBlocked",
        "awayMissed", "gameState", "endDateTime").filter(gameState__in=[5, 6, 7]).order_by('-gamePk')
    if cd['startDate'] is not None:
        games = games.filter(dateTime__date__gte=cd['startDate'])
    if cd['endDate'] is not None:
        games = games.filter(endDateTime__date__lte=cd['endDate'])
    if len(cd['gameTypes']) > 0:
        games = games.filter(gameType__in=cd['gameTypes'])
    if len(cd['venues']) > 0:
        games = games.filter(venue__in=cd['venues'])
    if len(cd['teams']) > 0:
        games = games.filter(Q(homeTeam__in=cd['teams']) | Q(awayTeam__in=cd['teams']))
    if len(cd['seasons']) > 0:
        games = games.filter(season__in=cd['seasons'])
    paginator = Paginator(games, 30)

    page = request.GET.get('page')
    try:
        games = paginator.page(page)
    except PageNotAnInteger:
        page = 1
        games = paginator.page(1)
    except EmptyPage:
        page = paginator.num_pages
        games = paginator.page(paginator.num_pages)
    page_range = games.paginator.page_range
    page = int(page)
    if len(page_range) > 5:
        tpr = []
        for p in page_range:
            if page - p <= 2 and page - p >= 0:
                tpr.append(p)
            elif p - page >= 1 and p - page <= 4:
                if len(tpr) < 5:
                    tpr.append(p)
                else:
                    break
        page_range = tpr

    context = {
        'active_page': 'games',
        'games': games,
        'form': form,
        'page': page,
        'page_range': page_range,
    }
    return render(request, 'games/game_list.html', context)
