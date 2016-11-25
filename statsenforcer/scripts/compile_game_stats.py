import os
import sys
import django

import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), "statsenforcer"))
sys.path.append("../")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "statsenforcer.settings")
from django.conf import settings
from django.db import transaction

django.setup()

from playbyplay.models import Game, PlayByPlay, PlayerGameStats, GoalieGameStats
from team.models import TeamGameStats

import queries

from fancystats import constants, team


def compile_info(game):
    with transaction.atomic():
        pbp = [x.__dict__ for x in PlayByPlay.objects.raw(queries.playbyplayquery, [game, ])]
        if len(pbp) > 0:
            homeTeam = pbp[0]["homeTeam_id"]
            awayTeam = pbp[0]["awayTeam_id"]
            playerteams = PlayerGameStats.objects.values("team__abbreviation", "team_id", "player_id", "player__fullName", "player__primaryPositionCode").filter(game_id=game)
            p2t = {}
            for p in playerteams:
                p2t[p["player_id"]] = [p["team__abbreviation"], p["team_id"], 0, p["player__fullName"], p["player__primaryPositionCode"]]
            goalieteams = GoalieGameStats.objects.values("team__abbreviation", "team_id", "player_id", "player__fullName", "player__primaryPositionCode").filter(game_id=game)
            for p in goalieteams:
                p2t[p["player_id"]] = [p["team__abbreviation"], p["team_id"], 1, p["player__fullName"], p["player__primaryPositionCode"]]
            for strength in constants.TEAMSTRENGTHS_CHOICES:
                s = strength[0]
                for scoresituation in constants.SCORESITUATION_CHOICES:
                    ss = scoresituation[0]
                    for period in constants.PERIOD_CHOICES:
                        p = period[0]
                        stats = team.get_stats(pbp, homeTeam, awayTeam, p2t, s, ss, p)
                        if stats[homeTeam]["toiseconds"] != 0:
                            calc_team_stats(stats, game, p, s, ss, homeTeam, awayTeam)
                        if stats[awayTeam]["toiseconds"] != 0:
                            calc_team_stats(stats, game, p, s, ss, awayTeam, homeTeam)


def calc_team_stats(stats, game, p, s, ss, team1, team2):
    tdata = stats[team1]
    tgs, created = TeamGameStats.objects.get_or_create(team_id=team1, game_id=game,
        period=p, teamstrength=s, scoresituation=ss)
    tgs.game_id = game
    tgs.team_id = team1
    tgs.period = p
    tgs.teamstrength = s
    tgs.scoresituation = ss
    tgs.toi = tdata["toiseconds"]
    tgs.scoringChancesFor = tdata["scf"]
    tgs.scoringChancesAgainst = stats[team2]["scf"]
    tgs.highDangerScoringChancesFor = tdata["hscf"]
    tgs.highDangerScoringChancesAgainst = stats[team2]["hscf"]
    tgs.offensiveZoneStartsFor = tdata["zso"]
    tgs.offensiveZoneStartsAgainst = stats[team2]["hscf"]
    tgs.faceoffWins = tdata["fo_w"]
    tgs.faceoffLosses = stats[team2]["fo_w"]
    tgs.shotsFor = tdata["sf"]
    tgs.shotsAgainst = stats[team2]["sf"]
    tgs.missedShotsFor = tdata["msf"]
    tgs.missedShotsAgainst = stats[team2]["msf"]
    tgs.blockedShotsFor = tdata["bsf"]
    tgs.blockedShotsAgainst = stats[team2]["bsf"]
    tgs.goalsFor = tdata["gf"]
    tgs.goalsAgainst = stats[team2]["gf"]
    tgs.penaltyFor = tdata["pn"]
    tgs.penaltyAgainst = stats[team2]["pn"]
    tgs.giveaways = tdata["give"]
    tgs.takeaways = tdata["take"]
    tgs.save()


def main():
    games = TeamGameStats.objects.values_list("game_id", flat=True).all()
    mgames = Game.objects.values_list("gamePk", flat=True).exclude(gamePk__in=games)\
        .filter(gameState__in=["5", "6", "7"], season=20162017)
    for game in mgames:
        print game
        compile_info(game)



if __name__ == "__main__":
    main()
