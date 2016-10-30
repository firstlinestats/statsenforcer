from django.shortcuts import render, get_object_or_404

import pytz

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
    teamStrengths = None
    scoreSituation = None
    hsc = None
    asc = None
    if request.method == "GET":
        context["form"] = forms.GameForm(request.GET)
        if context["form"].is_valid():
            cd = context["form"].cleaned_data
            teamStrengths = cd["teamstrengths"]
            scoreSituation = cd["scoresituation"]
    context["game"].dateTime = context["game"].dateTime.astimezone(pytz.timezone('US/Eastern'))
    try:
        context["period"] = models.GamePeriod.objects.filter(game_id=game_pk).latest("startTime")
    except:
        context["period"] = None
    if context["period"] is not None:
        context["playbyplay"] = models.PlayByPlay.objects.filter(gamePk_id=game_pk).order_by("eventIdx")
        context["playbyplay"] = [x.__dict__ for x in context["playbyplay"]]

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

        context["periodTimeString"] = str(context["playbyplay"][-1]["periodTime"])[:-3]
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
            hsc=hsc,
            asc=asc)
        for ts in context["teamstats"]:
            team = get_object_or_404(tmodels.Team, id=ts)
            context["teamstats"][ts]["team"] = team.abbreviation

        context["playerstats"] = fancystats.player.get_stats(context["playbyplay"], context["game"].homeTeam.id, context["game"].awayTeam.id, p2t)

        context["teamstats"] = context["teamstats"].values()
    return render(request, 'games/game.html', context)


def games(request):
    games = Game.objects.filter(season=20162017, gameState=6).order_by('-dateTime', '-gamePk')[:30]

    context = {
        'active_page': 'index',
        'games': games
    }
    return render(request, 'games/game_list.html', context)
