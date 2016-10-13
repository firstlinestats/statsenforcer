from django.shortcuts import render, get_object_or_404

import fancystats

from . import models
from team import models as tmodels

# Create your views here.
def game(request, game_pk):
    context = {}
    context["game"] = get_object_or_404(models.Game, gamePk=game_pk)
    try:
        context["period"] = models.GamePeriod.objects.filter(game_id=game_pk).latest("startTime")
    except:
        context["period"] = None
    if context["period"] is not None:
        context["playbyplay"] = models.PlayByPlay.objects.filter(gamePk_id=game_pk).order_by("eventIdx")
        context["periodTime"] = str(context["playbyplay"].last().periodTime)[:-3]
        pbpdict = [x.__dict__ for x in context["playbyplay"]]
        context["teamstats"] = fancystats.team.get_stats(pbpdict, context["game"].homeTeam.id, context["game"].awayTeam.id)
        for ts in context["teamstats"]:
            team = get_object_or_404(tmodels.Team, id=ts)
            context["teamstats"][ts]["team"] = team.abbreviation
        context["teamstats"] = context["teamstats"].values()
    return render(request, 'games/game.html', context)