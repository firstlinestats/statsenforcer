from django.shortcuts import render

from django.http import HttpResponse
from playbyplay.models import Game

def index(request):
    games = Game.objects.all()
    print games
    return HttpResponse("Hello, world. You're at the main page.")