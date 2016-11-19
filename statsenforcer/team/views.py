from django.shortcuts import render
from django.http import Http404
from team.models import Team
from player.models import Player
from datetime import date
import constants

def teams(request):
    teams = Team.objects.filter(active=1)
    context = {
        "teams" : teams
    }
    return render(request, 'team/teams.html', context)

def team_page(request, team_name):
    try:
        team_name = team_name.replace("-", " ")
        team = Team.objects.get(teamName=team_name, active=1)
        players = Player.objects.filter(currentTeam__exact=team, ).order_by('lastName')

        # get player's current age
        for player in players:
            today = date.today()
            player.age = today.year - player.birthDate.year - (
            (today.month, today.day) < (player.birthDate.month, player.birthDate.day))

        if team.conference == 'E':
            team.conference = 'Eastern'
        elif team.conference == 'W':
            team.conference = 'Western'

        if team.division == 'M':
            team.division = "Metropolitan"
        elif team.division == 'A':
            team.division = 'Atlantic'
        elif team.division == 'P':
            team.division = 'Pacific'
        elif team.division == 'C':
            team.division = 'Central'

    except Team.DoesNotExist:
        raise Http404("Team does not exist!")
    return render(request, 'team/team_page.html', {
        'team': team,
        'players': players
    })
