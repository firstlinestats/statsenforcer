from django.shortcuts import render
from django.http import Http404
from team.models import Team, TeamGameStats
from player.models import Player
from datetime import date
import constants

from fancystats import toi, corsi


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

        tgs = TeamGameStats.objects.filter(team=team, period="all",
            teamstrength="all", scoresituation="all")
        stats = {}
        for row in tgs:
            season = row.game.season
            teamid = team.id
            if team.id not in stats:
                stats[team.id] = {}
            if row.game.season not in stats[team.id]:
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
                row["toi"] = toi.format_minutes(row["toi"] / row["games"])
                row["sc"] = '%.2f' % corsi.corsi_percent(row["scoringChancesFor"],
                    row["scoringChancesAgainst"])
                row["hsc"] = '%.2f' % corsi.corsi_percent(row["highDangerScoringChancesFor"],
                    row["highDangerScoringChancesAgainst"])
                row["zso"] = '%.2f' % corsi.corsi_percent(row["offensiveZoneStartsFor"],
                    row["offensiveZoneStartsAgainst"])
                row["fo_w"] = '%.2f' % corsi.corsi_percent(row["faceoffWins"], row["faceoffLosses"])
                row["sf"] = '%.2f' % corsi.corsi_percent(row["shotsFor"], row["shotsAgainst"])
                row["msf"] = '%.2f' % corsi.corsi_percent(row["missedShotsFor"],
                    row["missedShotsAgainst"])
                row["bsf"] = '%.2f' % corsi.corsi_percent(row["blockedShotsFor"],
                    row["blockedShotsAgainst"])
                row["gf"] = '%.2f' % corsi.corsi_percent(row["goalsFor"], row["goalsAgainst"])
                row["pn"] = '%.2f' % corsi.corsi_percent(row["penaltyFor"], row["penaltyAgainst"])
                if row["corsiFor"] is not None:
                    row["cf"] = '%.2f' % corsi.corsi_percent(row["corsiFor"], row["corsiAgainst"])
                    row["hit"] = '%.2f' % corsi.corsi_percent(row["hitsFor"], row["hitsAgainst"])


    except Team.DoesNotExist:
        raise Http404("Team does not exist!")
    return render(request, 'team/team_page.html', {
        'team': team,
        'players': players,
        'stats': stats,
    })
