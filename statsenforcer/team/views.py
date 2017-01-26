from django.shortcuts import render
from django.http import Http404, JsonResponse
from django.core.serializers.json import DjangoJSONEncoder
from team.models import Team, TeamGameStats
from player.models import Player
from playbyplay.models import Game
from playbyplay.forms import GameFilterForm, GameForm
from datetime import date, datetime
import constants
import json

import teamqueries

from fancystats import toi, corsi


def teams(request):
    teams = Team.objects.filter(active=1)
    context = {
        "teams" : teams
    }
    teamstrength = "even"
    scoresituation = "all"
    period = "all"
    currentSeason = Game.objects.latest("endDateTime").season
    seasons = [currentSeason, ]
    form = GameFilterForm()
    startDate = None
    endDate = None
    venues = []
    teams = []
    if request.method == 'GET':
        form = GameFilterForm(request.GET)
        if form.is_valid():
            cd = form.cleaned_data
            teamstrength = cd["teamstrengths"]
            scoresituation = cd["scoresituation"]
            period = cd["period"]
            startDate = cd["startDate"]
            endDate = cd["endDate"]
            venues = cd["venues"]
            teams = cd["teams"]
    gameids = Game.objects.values_list("gamePk", flat=True).filter(gameState__in=[5, 6, 7])
    if startDate is not None:
        gameids = gameids.filter(dateTime__date__gte=startDate)
    if endDate is not None:
        gameids = gameids.filter(dateTime__date__lte=endDate)
    if len(venues) > 0:
        gameids = gameids.filter(venue__in=venues)
    if len(teams) > 0:
        gameids = gameids.filter(Q(homeTeam__in=cd['teams']) | Q(awayTeam__in=cd['teams']))
    gameids = [x for x in gameids]
    # print [team.id for team in teams]
    tgs = TeamGameStats.objects.raw(teamqueries.teamsquery, [gameids, scoresituation, teamstrength, period, seasons])
    stats = {}
    start = datetime.now()
    for row in tgs:
        season = row.season
        teamid = row.team_id
        # print teamid
        if teamid not in stats:
            stats[teamid] = {}
        if season not in stats[teamid]:
            stats[teamid][season] = row.__dict__
            stats[teamid][season]["games"] = 1
            stats[teamid][season].pop("_state", None)
            stats[teamid][season].pop("game_id", None)
            stats[teamid][season].pop("period", None)
            stats[teamid][season].pop("teamstrength", None)
            stats[teamid][season].pop("scoresituation", None)
            stats[teamid][season].pop("team_id", None)
        else:
            stats[teamid][season]["games"] += 1
            for key in stats[teamid][season]:
                if key not in ["abbreviation", "shortName", "teamName"]:
                    try:
                        stats[teamid][season][key] += row.__dict__[key]
                    except:
                        pass
    # print datetime.now() - start
    for teamid in stats:
        for season in stats[teamid]:
            row = stats[teamid][season]
            row["toiSeconds"] = row["toi"] / row["games"]
            row["toi"] = toi.format_minutes(row["toi"] / row["games"])
            row["sc"] = '%.1f' % corsi.corsi_percent(row["scoringChancesFor"],
                row["scoringChancesAgainst"])
            row["hsc"] = '%.1f' % corsi.corsi_percent(row["highDangerScoringChancesFor"],
                row["highDangerScoringChancesAgainst"])
            row["zso"] = '%.1f' % corsi.corsi_percent(row["offensiveZoneStartsFor"],
                row["offensiveZoneStartsAgainst"])
            row["fo_w"] = '%.1f' % corsi.corsi_percent(row["faceoffWins"], row["faceoffLosses"])
            row["sf"] = '%.1f' % corsi.corsi_percent(row["shotsFor"], row["shotsAgainst"])
            row["msf"] = '%.1f' % corsi.corsi_percent(row["missedShotsFor"],
                row["missedShotsAgainst"])
            row["bsf"] = '%.1f' % corsi.corsi_percent(row["blockedShotsFor"],
                row["blockedShotsAgainst"])
            row["gf"] = '%.1f' % corsi.corsi_percent(row["goalsFor"], row["goalsAgainst"])
            row["pn"] = '%.1f' % corsi.corsi_percent(row["penaltyFor"], row["penaltyAgainst"])
            row["cf"] = '%.1f' % corsi.corsi_percent(row["corsiFor"], row["corsiAgainst"])
            row["hit"] = '%.1f' % corsi.corsi_percent(row["hitsFor"], row["hitsAgainst"])
    # print datetime.now() - start
    context["stats"] = stats
    context["form"] = form

    if request.method == "GET" and "format" in request.GET and request.GET["format"] == "json":
        context.pop("form")
        context.pop("teams")
        return JsonResponse(context)
    else:
        context["statsJson"] = json.dumps(stats, cls=DjangoJSONEncoder)
    return render(request, 'team/teams.html', context)

def team_page(request, team_name):
    try:
        form = GameForm()
        teamstrength = "even"
        scoresituation = "all"
        period = "all"
        if request.method == "GET":
            form = GameForm(request.GET)
            if form.is_valid():
                cd = form.cleaned_data
                teamstrength = cd["teamstrengths"]
                scoresituation = cd["scoresituation"]
                period = cd["period"]
        team_name = team_name.replace("-", " ")
        team = Team.objects.get(shortName=team_name, active=1)
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

        tgs = TeamGameStats.objects.raw(teamqueries.teamquery, [scoresituation, teamstrength, period, team.id])
        stats = {}
        start = datetime.now()
        for row in tgs:

            season = row.season
            teamid = team.id
            if team.id not in stats:
                stats[teamid] = {}
            if season not in stats[teamid]:
                stats[teamid][season] = row.__dict__
                stats[teamid][season]["games"] = 1
                stats[teamid][season].pop("_state", None)
                stats[teamid][season].pop("game_id", None)
                stats[teamid][season].pop("period", None)
                stats[teamid][season].pop("teamstrength", None)
                stats[teamid][season].pop("scoresituation", None)
                stats[teamid][season].pop("team_id", None)
            else:
                stats[teamid][season]["games"] += 1
                for key in stats[teamid][season]:
                    try:
                        stats[teamid][season][key] += row.__dict__[key]
                    except:
                        pass
        for teamid in stats:
            for season in stats[teamid]:
                row = stats[teamid][season]
                row["shortName"] = team.shortName
                row["teamName"] = team.teamName
                row["abbreviation"] = team.abbreviation
                row["toiSeconds"] = row["toi"] / row["games"]
                row["toi"] = toi.format_minutes(row["toi"] / row["games"])
                row["sc"] = '%.1f' % corsi.corsi_percent(row["scoringChancesFor"],
                    row["scoringChancesAgainst"])
                row["hsc"] = '%.1f' % corsi.corsi_percent(row["highDangerScoringChancesFor"],
                    row["highDangerScoringChancesAgainst"])
                row["zso"] = '%.1f' % corsi.corsi_percent(row["offensiveZoneStartsFor"],
                    row["offensiveZoneStartsAgainst"])
                row["fo_w"] = '%.1f' % corsi.corsi_percent(row["faceoffWins"], row["faceoffLosses"])
                row["sf"] = '%.1f' % corsi.corsi_percent(row["shotsFor"], row["shotsAgainst"])
                row["msf"] = '%.1f' % corsi.corsi_percent(row["missedShotsFor"],
                    row["missedShotsAgainst"])
                row["bsf"] = '%.1f' % corsi.corsi_percent(row["blockedShotsFor"],
                    row["blockedShotsAgainst"])
                row["gf"] = '%.1f' % corsi.corsi_percent(row["goalsFor"], row["goalsAgainst"])
                row["pn"] = '%.1f' % corsi.corsi_percent(row["penaltyFor"], row["penaltyAgainst"])
                row["cf"] = '%.1f' % corsi.corsi_percent(row["corsiFor"], row["corsiAgainst"])
                row["hit"] = '%.1f' % corsi.corsi_percent(row["hitsFor"], row["hitsAgainst"])

        context = {
            'team': team,
            'players': players,
            'stats': stats,
            'statsJson': stats,
            'form': form,
        }
        if request.method == "GET" and "format" in request.GET and request.GET["format"] == "json":
            context['players'] = [x.__dict__ for x in context["players"]]
            [x.pop("_state", None) for x in context["players"]]
            context["team"] = context["team"].__dict__
            context["team"].pop("_state", None)
            context.pop("form")
            return JsonResponse(context)
        else:
            context["statsJson"] = json.dumps(stats, cls=DjangoJSONEncoder)

    except Team.DoesNotExist:
        raise Http404("Team does not exist!")
    return render(request, 'team/team_page.html', context)
