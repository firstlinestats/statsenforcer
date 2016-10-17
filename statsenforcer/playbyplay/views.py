from django.shortcuts import render, get_object_or_404

import fancystats

from . import models
from . import forms
from team import models as tmodels

# Create your views here.
def game(request, game_pk):
    context = {}
    context["game"] = get_object_or_404(models.Game, gamePk=game_pk)
    context["form"] = forms.GameForm()
    try:
        context["period"] = models.GamePeriod.objects.filter(game_id=game_pk).latest("startTime")
    except:
        context["period"] = None
    if context["period"] is not None:
        context["playbyplay"] = models.PlayByPlay.objects.filter(gamePk_id=game_pk).order_by("eventIdx")
        context["playbyplay"] = [x.__dict__ for x in context["playbyplay"]]

        poi_data = models.PlayerOnIce.objects.values("player_id", "play_id", "play__homeScore", "play__awayScore", "player__fullName").filter(play_id__in=[x["id"] for x in context["playbyplay"]])

        playerteams = models.PlayerGameStats.objects.values("team__abbreviation", "team_id", "player_id").filter(game_id=game_pk)
        p2t = {}
        for p in playerteams:
            p2t[p["player_id"]] = [p["team__abbreviation"], p["team_id"], 0]
        goalieteams = models.GoalieGameStats.objects.values("team__abbreviation", "team_id", "player_id").filter(game_id=game_pk)
        for p in goalieteams:
            p2t[p["player_id"]] = [p["team__abbreviation"], p["team_id"], 1]

        pip_data = models.PlayerInPlay.objects.values("player_type", "play_id", "player__fullName", "player__primaryPositionCode", "player_id").filter(play_id__in=[x["id"] for x in context["playbyplay"]])
        pipdict = {}
        for poi in pip_data:
            p2t[poi["player_id"]].append(poi["player__fullName"])
            p2t[poi["player_id"]].append(poi["player__primaryPositionCode"])
            if poi["play_id"] not in pipdict:
                pipdict[poi["play_id"]] = []
            if poi["player_id"] in p2t:
                poi["player__fullNameTeam"] = poi["player__fullName"] + " (" + p2t[poi["player_id"]][0] + ")"
            pipdict[poi["play_id"]].append(poi)

        context["periodTimeString"] = str(context["playbyplay"][-1]["periodTime"])[:-3]
        for play in context["playbyplay"]:
            play["periodTimeString"] = str(play["periodTime"])[:-3]
            if play["id"] in pipdict:
                play["players"] = pipdict[play["id"]]
            else:
                play["players"] = []
        
        context["teamstats"] = fancystats.team.get_stats(context["playbyplay"], context["game"].homeTeam.id, context["game"].awayTeam.id, p2t)
        for ts in context["teamstats"]:
            team = get_object_or_404(tmodels.Team, id=ts)
            context["teamstats"][ts]["team"] = team.abbreviation

        context["playerstats"] = fancystats.player.get_stats(context["playbyplay"], context["game"].homeTeam.id, context["game"].awayTeam.id, p2t)

        context["teamstats"] = context["teamstats"].values()
    return render(request, 'games/game.html', context)