from django.shortcuts import render, get_object_or_404

from . import models

# Create your views here.
def game(request, game_pk):
    context = {}
    context["game"] = get_object_or_404(models.Game, gamePk=game_pk)
    try:
        context["period"] = models.GamePeriod.objects.filter(game_id=game_pk).latest("startTime")
    except:
        context["period"] = None
    return render(request, 'game/game.html', context)