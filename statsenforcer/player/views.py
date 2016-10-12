from django.shortcuts import render
from django.http import Http404
from team.models import Team
from player.models import Player
from datetime import date


def players(request):
    return render(request, 'players/players.html')

def player_page(request, player_id):
    return render(request, 'players/player_page.html')