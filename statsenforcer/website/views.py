from django.shortcuts import render

from django.http import HttpResponse
from team.models import Team

def index(request):
    teams = Team.objects.all()
    print teams
    return HttpResponse("Hello, world. You're at the main page.")