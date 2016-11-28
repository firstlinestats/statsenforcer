import os
import sys
import django

import datetime
import linecache

sys.path.append(os.path.join(os.path.dirname(__file__), "statsenforcer"))
sys.path.append("../")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "statsenforcer.settings")
from django.conf import settings
from django.db import transaction

django.setup()

from playbyplay.models import Game, PlayByPlay, PlayerGameStats, GoalieGameStats, PlayerOnIce, PlayerInPlay
from team.models import TeamGameStats
from player.models import PlayerGameFilterStats

import queries

from fancystats import constants, team, player
import sendemail


def compile_info(game):
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
        pip_data = PlayerInPlay.objects.values("player_type", "play_id", "player__fullName", "player__primaryPositionCode", "player_id").filter(play_id__in=[x["id"] for x in pbp])
        pipdict = {}
        for poi in pip_data:
            if poi["play_id"] not in pipdict:
                pipdict[poi["play_id"]] = []
            if poi["player_id"] in p2t:
                poi["player__fullNameTeam"] = poi["player__fullName"] + " (" + p2t[poi["player_id"]][0] + ")"
            pipdict[poi["play_id"]].append(poi)
        poi_data = PlayerOnIce.objects.values("player_id", "play_id", "player__lastName", "player__primaryPositionCode").filter(play_id__in=[x["id"] for x in pbp])
        poidict = {}
        for poi in poi_data:
            poi["team_id"] = p2t[poi["player_id"]][1]
            if poi["play_id"] not in poidict:
                poidict[poi["play_id"]] = []
            poidict[poi["play_id"]].append(poi)
        order = ["L", "C", "R", "D", "G"]
        for play in poidict:
            poidict[play] = sorted(poidict[play], key=lambda x: order.index(x["player__primaryPositionCode"]))
        for play in pbp:
            play["periodTimeString"] = str(play["periodTime"])[:-3]
            if play["id"] in pipdict:
                play["players"] = pipdict[play["id"]]
            else:
                play["players"] = []
            if play["id"] in poidict:
                play["onice"] = poidict[play["id"]]
            else:
                play["onice"] = []

        with transaction.atomic():
            total = len(constants.TEAMSTRENGTHS_CHOICES) * len(constants.SCORESITUATION_CHOICES) * len(constants.PERIOD_CHOICES)
            count = 0
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
                        pstats = player.get_stats(pbp, homeTeam, awayTeam, p2t, s, ss, p)
                        for teamid in pstats:
                            for playerid in pstats[teamid]:
                                pstat = pstats[teamid][playerid]
                                if pstat["toiseconds"] != 0:
                                    calc_player_stats(pstat, playerid, game, teamid, p, s, ss)


def calc_player_stats(stats, pid, game, team, p, s, ss):
    tgs, created = PlayerGameFilterStats.objects.get_or_create(player_id=pid, game_id=game, team_id=team,
        period=p, teamstrength=s, scoresituation=ss)
    tgs.player_id = pid
    tgs.game_id = game
    tgs.team_id = team
    tgs.period = p
    tgs.teamstrength = s
    tgs.scoresituation = ss
    tgs.toi = stats["toiseconds"]
    tgs.goals = stats["g"]
    tgs.assists1 = stats["a1"]
    tgs.assists2 = stats["a2"]
    tgs.points = stats["p"]
    tgs.corsiFor = stats["cf"]
    tgs.corsiAgainst = stats["ca"]
    tgs.fenwickFor = stats["ff"]
    tgs.fenwickAgainst = stats["fa"]
    tgs.goalsFor = stats["gf"]
    tgs.goalsAgainst = stats["ga"]
    tgs.fo_w = stats["fo_w"]
    tgs.fo_l = stats["fo_l"]
    tgs.hitFor = stats["hitplus"]
    tgs.hitAgainst = stats["hitminus"]
    tgs.penaltyFor = stats["pnplus"]
    tgs.penaltyAgainst = stats["pnminus"]
    tgs.scoringChancesFor = stats["scf"]
    tgs.scoringChancesAgainst = stats["sca"]
    tgs.highDangerScoringChancesFor = stats["hscf"]
    tgs.highDangerScoringChancesAgainst = stats["hsca"]
    tgs.individualShotsBlocked = stats["bk"]
    tgs.offensiveZoneStarts = stats["zso"]
    tgs.neutralZoneStarts = stats["zsn"]
    tgs.defensiveZoneStarts = stats["zsd"]
    tgs.shotsFor = stats["onsf"]
    tgs.shotsAgainst = stats["onsa"]
    tgs.missedShotsFor = stats["onmsf"]
    tgs.missedShotsAgainst = stats["onmsa"]
    tgs.blockedShotsFor = stats["onbsf"]
    tgs.blockedShotsAgainst = stats["onbsa"]
    tgs.individualShots = stats["sf"]
    tgs.individualMissedShots = stats["msf"]
    tgs.individualBlockedShots = stats["bsf"]
    tgs.individualScoringChances = stats["isc"]
    tgs.individualHighDangerScoringChances = stats["ihsc"]
    tgs.save()


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
    tgs.hitsFor = tdata["hit"]
    tgs.hitsAgainst = stats[team2]["hit"]
    tgs.corsiFor = tdata["cf"]
    tgs.corsiAgainst = stats[team2]["cf"]
    tgs.save()


def main():
    emailssent = 0
    existing = set(PlayerGameFilterStats.objects.values_list("game_id", flat=True).distinct())
    existing = []
    mgames = Game.objects.values_list("gamePk", flat=True)\
        .filter(gameState__in=["5", "6", "7"]).exclude(gameType="PR").exclude(gamePk__in=existing).order_by("-gamePk")
    for game in mgames:
        try:
            compile_info(game)
        except Exception as e:
            if emailssent < 5:
                exc_type, exc_obj, tb = sys.exc_info()
                f = tb.tb_frame
                lineno = tb.tb_lineno
                filename = f.f_code.co_filename
                linecache.checkcache(filename)
                line = linecache.getline(filename, lineno, f.f_globals)
                message = 'GAME: {}, EXCEPTION IN ({}, LINE {} "{}"): {}'.format(game, filename, lineno, line.strip(), exc_obj)
                sendemail.send_error_email(message)
                emailssent += 1
                #raise Exception(e)


if __name__ == "__main__":
    main()
    #compile_info(2016020001)
