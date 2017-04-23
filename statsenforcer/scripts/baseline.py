import os
import sys
import json
import glob
import time
import django

from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), "statsenforcer"))
sys.path.append("../")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "statsenforcer.settings")
from django.conf import settings

django.setup()

import api_calls

import team.models as tmodels
import player.models as pmodels
import playbyplay.models as pbpmodels
import website.models as wmodels
from django.db import transaction

import fancystats

def main():
    #ingest_teams()
    #ingest_players()
    #ingest_games()

    #ingest_pbp()

    #getAwayShots()
    #getMissedShots()
    #findTeam()
    #findStandings(20152016)
    #findBirthState()
    ingest_glossary()


def ingest_glossary():
    gterms = {'OCOn%': ' On-ice Corsi On-goal percentage; The percentage of on-ice shot attempts (on goal, missed, or blocked) that are shots on goal.', 'Shots.All': ' The number of shots faced by the goalie from all zones in Hextally.', 'SCA': ' Scoring chances Against; The number of scoring chances for the opposing team. For players, calculated using on-ice events.', 'OCAOn%': ' On-ice Corsi Against On-goal percentage; The percentage of on-ice shot attempts (on goal, missed, or blocked) by the opposing team that are shots on goal.', 'SCF%Rel': ' Relative Scoring Chance percentage; The player\'s on-ice SCF% minus the player\'s off-ice SCF%.', 'FF%': ' Fenwick percentage; The percentage of total unblocked shot attempts (on goal or missed) taken by the team. For players, calculated using on-ice events.', 'SF%': ' Shot percentage; The percentage of total shots on goal taken by the team. For players, calculated using on-ice events.', 'CorT%': " Corsi Quality of Teammates; The TOI-weighted CF% for a player's teammates.", 'Scoring Chance': ' Please refer to the definition here', 'GAB.Net': " Net goals above baseline (GAB.Offense - GAB.Defense + GAB.PPNet + GAB.SHNet); for more information, see Andrew's Road to War blog post.", 'C+/-': ' Corsi plus-minus; plus-minus for shot attempts (on goal, missed, or blocked). For players, calculated using on-ice events.', 'iFF': ' Individual Fenwick For; The number of unblocked shot attempts (on goal or missed) taken by an individual player.', 'SF': ' Shots For; The number of shots on goal taken by the team. For players, calculated using on-ice events.', 'League-Wide Success Rate': ' The league-wide shooting percentage from that area of the ice in the time frame selected.', 'tCF60': " CF60 Quality of Teammates; The TOI-weighted CF60 for a player's teammates.", 'Shot Rate Differential': ' The difference between Team Shot Rate For and Team Shot Rate Against.', 'GF': ' Goals For; The number of goals scored by the team. For players, calculated using on-ice events.', 'Team Shot Rate Against (Relative)': ' For players', 'GA': ' Goals Against; The number of goals scored by the opposing team. For players, calculated using on-ice events.', 'GF60': ' Goals For per 60; The rate of goals scored by the eam per 60 minutes of play. For players, calculated using on-ice events.', 'Shooting % For Goal (Relative)': " A team's shooting percetance for goal relative to the league-wide success rate in that area of the ice. Values above 0 are better than average, while values below 0 are worse than average.", 'Save Percentage Zones': ' blue = high percentage shots (Sv%H), red = medium percentage shots (Sv%M), yellow = low-percentage shots (Sv%L).', 'Color By Statistical Significance': " If checked, colors will be adjusted on to a scale of 0 +/- 8. Dark red colors mean that (e.g.) the player's team's shot rate is significantly better than league-average with the player on the ice. Dark blue colors mean that (e.g.) the player's team's shot rate is significantly worse than league-average with that player on the ice.", 'Sh%': ' Shooting percentage; The percentage of shots on goal that are goals.', 'CP60': ' Corsi Pace per 60; The sum of CF60 and CA60. For players, calculated using on-ice events.', 'SCA60': ' Scoring chances Against per 60; The rate of scoring chances for the opposing team per 60 minutes of play. For players, calculated using on-ice events.', 'CF%Rel': " Relative Corsi percentage; The player's on-ice CF% minus the player's off-ice CF%.", 'HSCA': ' High-danger Scoring Chances Against; The number of High-danger Scoring Chances for the opposing team. For players, calculated using on-ice events.', 'HSCF': ' High-danger Scoring Chances For; The number of High-danger Scoring Chances for the team. For players, calculated using on-ice events.', 'F+/-': ' Fenwick plus-minus; plus-minus for unblocked shot attempts (on goal or missed). For players, calculated using on-ice events.', 'FF60': ' Fenwick For per 60; The rate of unblocked shot attempts (on goal or missed) taken by the team per 60 minutes of play. For players, calculated using on-ice events.', 'SCF': ' Scoring chances For; The number of scoring chances for the team. For players, calculated using on-ice events.', 'AdSv%': ' Adjusted save percentage; The weighted-average of Sv%H, Sv%M, and Sv%L, where the weights correspond to the league-average percentage of shots from each of those areas.', 'SA60': ' Shots Against per 60; The rate of shots on goal taken by the opposing team per 60 minutes of play. For players, calculated using on-ice events.', 'HSC+/-': ' Scoring Chance plus-minus; Plus-minus for High-danger Scoring Chances. For players, calculated using on-ice events. Scoring Chance definitions here', 'iSC': ' Individual Scoring Chances; The number of Scoring Chances recorded by an individual player.', 'iSF': ' Individual Shots For; The number of shots on goal taken by an individual player.', 'SC+/-': ' Scoring Chance plus-minus; Plus-minus for Scoring Chances. For players, calculated using on-ice events.', 'Sv%L': ' Low-Danger Save Percentage; Save percentage on low-percentage shots.', 'Sv%M': ' Medium-Danger Save Percentage; Save percentage on medium-percentage shots.', 'tCA60': " CA60 Quality of Teammates; The TOI-weighted CA60 for a player's teammates.", 'Sv%H': ' High-Danger Save Percentage; Save percentage on high-percentage shots.', 'SF60': ' Shots For per 60; The rate of shots on goal taken by the team per 60 minutes of play. For players, calculated using on-ice events.', 'FP60': ' Fenwick Pace per 60; The sum of FF60 and FA60. For players, calculated using on-ice events.', 'SCF60': ' Scoring chances For per 60; The rate of scoring chances for the team per 60 minutes of play. For players, calculated using on-ice events.', 'Shooting Rate (Relative)': " A team's rate of shots on goal from that area of the ice relative to league-average.", 'Saves.All': ' The number of saves made by the goalie on shots from all zones in Hextally.', 'ZSO%': ' Offensive Zone Start percentage; The percentage of all non-neutral zone faceoffs taken in the offensive zone.', 'cCF60': " CF60 Quality of Competition; The TOI-weighted CF60 for a player's competition.", 'SF%Rel': " Relative Shot percentage; The player's on-ice SF% minus the player's off-ice SF%.", 'nhlscrapr': " An open-source R package, written by Andrew and Sam, that can be used to compile NHL RTSS data from 2002 through present. For more, see Andrew's original blog post about nhlscrapr or the nhlscrapr package on CRAN. For instructions on how to use the package, see Andrew's more recent blog post.", 'PenD60': ' Penalty Differential per 60; Penalties drawn per 60 minutes of play minus penalties taken per 60 minutes of play.', 'FA': ' Fenwick Against; The number of unblocked shot attempts (on goal or missed) taken by the opposing team. For players, calculated using on-ice events.', 'cCA60': " CA60 Quality of Competition; The TOI-weighted CA60 for a player's competition.", 'FF': ' Fenwick For; The number of unblocked shot attempts (on goal or missed) taken by the team. For players, calculated using on-ice events.', 'FA60': ' Fenwick Against per 60; The rate of unblocked shot attempts (on goal or missed) taken by the opposing team per 60 minutes of play. For players, calculated using on-ice events.', 'S+/-': ' Shot plus-minus; plus-minus for shots on goal. For players, calculated using on-ice events.', 'GAB.PPNet': " Net power-play goals above baseline (power-play goals scored - short-handed goals allowed); for more information, see Andrew's Road to War blog post.", 'OFOn%': ' On-ice Fenwick On-goal percentage; The percentage of on-ice unblocked shot attempts (on goal or missed) that are shots on goal.', 'Saves.Perimeter': ' The number of saves made by the goalie on shots from the perimeter zones in Hextally.', 'HSCF60': ' High-danger Scoring Chances For per 60; The rate of High-danger Scoring Chances for the team per 60 minutes of play. For players, calculated using on-ice events.', 'Net Shots For': ' The number of on-ice shots on goal for that player/team.', 'Hextally': " A system for visualizing the locations and success rates shot attempts for players and teams using hexagonal bin plots. See Andrew's blog post for more.", 'Goals.Slot': ' The number of goals scored on the goalie on shots from the slot zones in Hextally.', 'Team Shot Rate For (Relative)': ' For players', 'Sv%': ' Save percentage; The percentage of shots on goal saved by the goaltender.', 'Goals.Perimeter': ' The number of goals scored on the goalie on shots from the perimeter zones in Hextally.', 'CA': ' Corsi Against; The number of shot attempts (on goal, missed, or blocked) taken by the opposing team. For players, calculated using on-ice events.', 'CF': ' Corsi For; The number of shot attempts (on goal, missed, or blocked) taken by the team. For players, calculated using on-ice events.', 'GAB.SHNet': " Net short-handed goals above baseline (short-handed goals scored - power-play goals allowed); for more information, see Andrew's Road to War blog post.", 'PDO': ' The sum of shooting percentage and save percentage. For players, calculated using on-ice events.', 'G+/-': ' Goal plus-minus; plus-minus for goals. For players, calculated using on-ice events.', 'FenSh%': ' Fenwick Shooting percentage; The percentage of unblocked shot attempts (on goal or missed) that are goals.', 'GAB.Defense': " Goals against above baseline; for more information, see Andrew's Road to War blog post.", 'Saves.Slot': ' The number of saves made by the goalie on shots from the slot zones in Hextally.', 'iCF': ' Individual Corsi For; The number of shot attempts (on goal, missed, or blocked) taken by an individual player.', 'TOI': ' Time On Ice.', 'Close': ' Refers to situations when teams are within 1 goal of one another in the 1st and 2nd periods or tied in the 3rd period or overtime.', 'SA': ' Shots Against; The number of shots on goal taken by the opposing team. For players, calculated using on-ice events.', 'GA60': ' Goals Against per 60; The rate of goals scored by the opposing team per 60 minutes of play. For players, calculated using on-ice events.', 'CA60': ' Corsi Against per 60; The rate of shot attempts (on goal, missed, or blocked) taken by the opposing team per 60 minutes of play. For players, calculated using on-ice events.', 'HSCA60': ' High-danger Scoring Chances Against per 60; The rate of High-danger Scoring Chances for the opposing team per 60 minutes of play. For players, calculated using on-ice events.', 'Player Shooting % For Goal': " The player's personal shooting percentage for goal from that area of the ice.", 'FenSv%': ' Fenwick Save percentage; The percentage of unblocked shot attempts (on goal or missed) that are saved by the goaltender or miss the net.', 'HSCP60': ' Scoring Chance Pace per 60; The sum of HSCF60 and HSCA60. For players, calculated using on-ice events.', 'CF%': ' Corsi percentage; The percentage of total shot attempts (on goal, missed, or blocked) taken by the team. For players, calculated using on-ice events.', 'TOIT%': " TOI Quality of Teammates; The TOI-weighted TOI% for a player's teammates.", 'SCP60': ' Scoring Chance Pace per 60; The sum of SCF60 and SCA60. For players, calculated using on-ice events.', 'AAV': ' Average Annual Value.', 'Net Shots Against': ' The number of on-ice shots on goal for the opposing team.', 'Saves.HomePlate': ' The number of saves made by the goalie on shots from the home plate zones in Hextally.', 'GF%': ' Goal percentage; The percentage of total goals scored by the team. For players, calculated using on-ice events.', 'CF60': ' Corsi For per 60; The rate of shot attempts (on goal, missed, or blocked) taken by the team per 60 minutes of play. For players, calculated using on-ice events.', 'Goals.All': ' The number of goals scored on the goalie on shots from all zones in Hextally.', 'PenD': ' Penalty Differential; Penalties drawn minus penalties taken.', 'TOIC%': " TOI Quality of Competition; The TOI-weighted TOI% for a player's competition.", 'Goals.HomePlate': ' The number of goals scored on the goalie on shots from the home plate zones in Hextally.', 'HSCF%': ' Scoring Chance percentage; The percentage of total High-danger Scoring Chances belonging to the team. For players, calculated using on-ice events.', 'GAB.Offense': " Goals for above baseline; for more information, see Andrew's Road to War blog post.", 'SCF%': ' Scoring Chance percentage; The percentage of total scoring chances belonging to the team. For players, calculated using on-ice events.', 'Shooting % For Goal (Absolute)': " A team's shooting percentage for goal in that area of the ice, unadjusted for the league-wide success rate.", 'GF%Rel': " Relative Goal percentage; The player's on-ice GF% minus the player's off-ice GF%.", 'Numbers On Plot': ' Adds statistical significance test statistics to the plot. Regardless of whether "Color By Statistical Significance" is checked, these numbers are test statistics for the following two-sided hypothesis test', 'FF%Rel': " Relative Fenwick percentage; The player's on-ice FF% minus the player's off-ice FF%.", 'Use Only Three Blocks': ' The default Hextally setting divides the rink into 9 areas of the ice (see graphic at bottom of the page). "Use Only Three Blocks" divides the ice into three areas, which correspond to high, medium, and low probabilities of shot success (shooting percentages).', 'ZSO%Rel': ' Relative Offensive Zone Start percentage; The player\'s on-ice ZSO% minus the player\'s off-ice ZSO%.', 'CorC%': " Corsi Quality of Competition; The TOI-weighted CF% for a player's competition.", 'OFAOn%': ' On-ice Fenwick Against On-goal percentage; The percentage of on-ice unblocked shot attempts (on goal or missed) by the opposing team that are shots on goal.', 'High-danger Scoring Chance': ' Please refer to the definition here', 'HSCF%Rel': ' Relative Scoring Chance percentage; The player\'s on-ice HSCF% minus the player\'s off-ice HSCF%.'}
    for key in gterms:
        gterm = wmodels.GlossaryTerm()
        gterm.key = key
        gterm.value = gterms[key]
        gterm.save()


@transaction.atomic
def findBirthState():
    for player in pmodels.Player.objects.all():
        j = json.loads(api_calls.get_player(player.id))
        p = j["people"][0]
        if "birthStateProvince" in p:
            player.birthStateProvince = p["birthStateProvince"]
            player.save()


@transaction.atomic
def findStandings(season):
    j = json.loads(api_calls.get_standings())
    for record in j["records"]:
        division = record["division"]["name"][0]
        conference = record["division"]["name"][0]
        for team in record["teamRecords"]:
            stat = tmodels.SeasonStats()
            stat.team_id = team["team"]["id"]
            stat.season = season
            stat.goalsAgainst = team["goalsAgainst"]
            stat.goalsScored = team["goalsScored"]
            stat.points = team["points"]
            stat.gamesPlayed = team["gamesPlayed"]
            stat.wins = team["leagueRecord"]["wins"]
            stat.losses = team["leagueRecord"]["losses"]
            stat.ot = team["leagueRecord"]["ot"]
            stat.date = datetime.now()
            try:
                stat.streakCode = team["streak"]["streakCode"]
            except:
                pass
            stat.save()



@transaction.atomic
def findTeam():
    game_data = {}
    count = 0
    playerlist = pbpmodels.PlayerGameStats.objects.order_by("game")
    plength = len(playerlist)
    for player in playerlist:
        count += 1
        if count % 100 == 0:
            print count, plength
        gamePk = player.game.gamePk
        if gamePk not in game_data:
            print gamePk
            j = json.loads(api_calls.get_game(gamePk))
            j = j["liveData"]
            game_data[gamePk] = {}
            allplayers = ["goalies", "skaters", "onIce", "scratches"]
            game_data[gamePk]["away"] = set()
            game_data[gamePk]["home"] = set()
            game_data[gamePk]["homegoalies"] = j["boxscore"]["teams"]["home"]["players"]
            game_data[gamePk]["awaygoalies"] = j["boxscore"]["teams"]["away"]["players"]
            game_data[gamePk]["awayteam"] = j["boxscore"]["teams"]["away"]["team"]["id"]
            game_data[gamePk]["hometeam"] = j["boxscore"]["teams"]["home"]["team"]["id"]
            game_data[gamePk]["period"] = j["linescore"]["currentPeriod"]
            for p in allplayers:
                game_data[gamePk]["away"].update(j["boxscore"]["teams"]["away"][p])
                game_data[gamePk]["home"].update(j["boxscore"]["teams"]["home"][p])
        """if player.player.id in game_data[gamePk]["away"]:
            player.team_id = game_data[gamePk]["awayteam"]
        elif player.player.id in game_data[gamePk]["home"]:
            player.team_id = game_data[gamePk]["hometeam"]
        else:
            print player.player.id, game_data[gamePk]["away"]
            print player.player.id, game_data[gamePk]["home"]
            raise Exception
        player.save()"""
    for gamePk in game_data:
        gd = game_data[gamePk]
        checkGoalies(gd["homegoalies"], gamePk, gd["hometeam"], gd["period"])
        checkGoalies(gd["awaygoalies"], gamePk, gd["awayteam"], gd["period"])


@transaction.atomic()
def checkGoalies(players, gamePk, team, period):
    for player in players:
        playerstats = players[player]["stats"]
        if "goalieStats" in playerstats:
            gs = playerstats["goalieStats"]
            goalie = pbpmodels.GoalieGameStats()
            goalie.player_id = int(player.replace("ID", ""))
            goalie.game_id = gamePk
            goalie.team_id = team
            goalie.period = period
            if gs["timeOnIce"] < "60:00" or len(gs["timeOnIce"]) < 5:
                goalie.timeOnIce = "00:" + gs["timeOnIce"]
            elif len(gs["timeOnIce"]) >= 8:
                goalie.timeOnIce = gs["timeOnIce"]
            else:
                minutes = str(int(gs["timeOnIce"][:2]) - 60)
                if len(minutes) == 1:
                    minutes = "0" + minutes
                goalie.timeOnIce = "01:" + minutes + gs["timeOnIce"][2:]
            goalie.assists = gs["assists"]
            goalie.goals = gs["goals"]
            goalie.pim = gs["pim"]
            goalie.shots = gs["shots"]
            goalie.saves = gs["saves"]
            goalie.powerPlaySaves = gs["powerPlaySaves"]
            goalie.shortHandedSaves = gs["shortHandedSaves"]
            goalie.shortHandedShotsAgainst = gs["shortHandedShotsAgainst"]
            goalie.evenShotsAgainst = gs["evenShotsAgainst"]
            goalie.evenSaves = gs["evenSaves"]
            goalie.powerPlayShotsAgainst = gs["powerPlayShotsAgainst"]
            goalie.decision = gs["decision"]
            goalie.save()


@transaction.atomic
def checkOT():
    for play in pbpmodels.PlayByPlay.objects.filter(period=5):
        game = play.gamePk
        if play.playType == "MISSED_SHOT":
            if play.team == game.homeTeam:
                game.homeMissed -= 1
            elif play.team == game.awayTeam:
                game.awayMissed -= 1
            if game.gamePk == 2015020788:
                print game.homeMissed, game.awayMissed
            game.save()


@transaction.atomic
def getMissedShots():
    count = 0
    games = []
    saves = []
    start = datetime.now()
    for game in pbpmodels.Game.objects.all():
        if game.gameState not in ["1", "2", "8", "9"]:
            count += 1
            try:
                j = json.loads(api_calls.get_game(game.gamePk))
                ld = j["liveData"]
                # Plays
                homeMissed = 0
                awayMissed = 0
                tpbp = pbpmodels.PlayByPlay.objects.filter(gamePk_id=game.gamePk)
                pbp = {}
                for t in tpbp:
                    pbp[t.eventId] = t
                teamid = None
                missed = None
                for play in ld["plays"]["allPlays"]:
                    eventId = play["about"]["eventIdx"]
                    if eventId in pbp and "team" in play:
                        pbp[eventId].team_id = play["team"]["id"]
                        saves.append(pbp[eventId])
                        if play["result"]["eventTypeId"] == "MISSED_SHOT":
                            if play["team"]["id"] == game.homeTeam_id:
                                homeMissed += 1
                            else:
                                awayMissed += 1
                game.homeMissed = homeMissed
                game.awayMissed = awayMissed
                games.append(game)
            except Exception as e:
                print e
                print "ISSUE WITH " + str(game.gamePk)
        if count % 100 == 0:
            print count, datetime.now() - start
            with transaction.atomic():
                for g in games:
                    g.save()
                for s in saves:
                    s.save()
                games = []
                saves = []
            print count, datetime.now() - start
    for g in games:
        g.save()
    for s in saves:
        s.save()


@transaction.atomic
def getAwayShots():
    for game in pbpmodels.Game.objects.all().order_by("gamePk"):
        with transaction.atomic():
            print game.gamePk
            j = json.loads(api_calls.get_game(game.gamePk))
            ld = j["liveData"]
            lineScore = ld["linescore"]
            game.awayShots = lineScore["teams"]["away"]["shotsOnGoal"]
            game.save()


@transaction.atomic()
def ingest_pbp():
    players = {}
    playid = 0
    tplayers = pmodels.Player.objects.all()
    for t in tplayers:
        players[t.id] = t
    count = 0
    update = []
    for game in pbpmodels.Game.objects.all().order_by("gamePk"):
        allshootouts = []
        allperiods = []
        allplaybyplay = []
        allplayers = []
        allpgss = []
        count += 1
        if count % 100 == 0:
            print count, game.gamePk
        if game.gameState not in ["1", "2", "8", "9"]:
            homeMissed = 0
            awayMissed = 0
            try:
                j = json.loads(api_calls.get_game(game.gamePk))
                homeSkaters = j["liveData"]["boxscore"]["teams"]["home"]["skaters"]
                homeGoalies = j["liveData"]["boxscore"]["teams"]["home"]["goalies"]
                homeOnIce = j["liveData"]["boxscore"]["teams"]["home"]["onIce"]
                homeScratches = j["liveData"]["boxscore"]["teams"]["home"]["scratches"]
                awaySkaters = j["liveData"]["boxscore"]["teams"]["away"]["skaters"]
                awayGoalies = j["liveData"]["boxscore"]["teams"]["away"]["goalies"]
                awayOnIce = j["liveData"]["boxscore"]["teams"]["away"]["onIce"]
                awayScratches = j["liveData"]["boxscore"]["teams"]["away"]["scratches"]
                homeIds = set(homeSkaters + homeGoalies + homeOnIce + homeScratches)
                awayIds = set(awaySkaters + awayGoalies + awayOnIce + awayScratches)
                gd = j["gameData"]
                # Player Info
                pinfo = gd["players"]
                for sid in pinfo: # I swear that's not a Crosby reference
                    iid = int(sid.replace("ID", ""))
                    if iid not in players:
                        if iid in homeIds:
                            team = game.homeTeam
                        elif iid in awayIds:
                            team = game.awayTeam
                        else:
                            print iid, homeIds, awayIds
                            raise Exception
                        player = ingest_player(pinfo[sid], team.id)
                        players[player.id] = player
                # liveData
                ld = j["liveData"]
                lineScore = ld["linescore"]
                # Plays
                for play in ld["plays"]["allPlays"]:
                    about = play["about"]
                    pplayers = play["players"]
                    result = play["result"]
                    coordinates = play["coordinates"]
                    p = pbpmodels.PlayByPlay()
                    p.id = playid
                    p.gamePk = game
                    p.eventId = about["eventId"]
                    p.eventIdx = about["eventIdx"]
                    p.period = about["period"]
                    p.periodTime = about["periodTime"]
                    p.dateTime = about["dateTime"]
                    p.playType = result["eventTypeId"]
                    p.playDescription = result["description"]
                    if "team" in play:
                        p.team_id = play["team"]["id"]
                    if result["eventTypeId"] == "MISSED_SHOT":
                        if play["team"]["id"] == game.homeTeam_id:
                            homeMissed += 1
                        else:
                            awayMissed += 1
                    if "secondaryType" in result:
                        if p.playType == "PENALTY":
                            p.penaltyType = result["secondaryType"]
                        else:
                            p.shotType = result["secondaryType"]
                    if p.playType == "PENALTY":
                        p.penaltySeverity = result["penaltySeverity"]
                        p.penaltyMinutes = result["penaltyMinutes"]
                    if "strength" in result:
                        p.strength = result["strength"]["code"]
                    if "x" in coordinates:
                        p.xcoord = coordinates["x"]
                        p.ycoord = coordinates["y"]
                    p.homeScore = lineScore["teams"]["home"]["goals"]
                    p.awayScore = lineScore["teams"]["away"]["goals"]
                    allplaybyplay.append(p)
                    assist_found = False
                    for pp in pplayers:
                        poi = pbpmodels.PlayerInPlay()
                        poi.play_id = playid
                        poi.game = game
                        poi.player_id = pp["player"]["id"]
                        if assist_found is True and fancystats.player.get_player_type(pp["playerType"]) == 6:
                            poi.player_type = 16
                            poi.eventId = about["eventId"]
                            poi.game_id = game.gamePk
                            update.append(poi)
                        else:
                            poi.player_type = fancystats.player.get_player_type(pp["playerType"])
                            if poi.player_type == 6:
                                assist_found = True
                        allplayers.append(poi)
                    playid += 1
                # Update gameData
            except Exception as e:
                print e
                print "1ISSUE WITH " + str(game.gamePk)
        try:
            pass
            #pbpmodels.Shootout.objects.bulk_create(allshootouts)
            #pbpmodels.GamePeriod.objects.bulk_create(allperiods)
            #pbpmodels.PlayByPlay.objects.bulk_create(allplaybyplay)
            #pbpmodels.PlayerInPlay.objects.bulk_create(allplayers)
            #pbpmodels.PlayerGameStats.objects.bulk_create(allpgss)
        except Exception as e:
            print e
            print "2ISSUE WITH " + str(game.gamePk)
    print "updating existing assists"
    for u in update:
        existing = pbpmodels.PlayerInPlay.objects.filter(play__eventId=u.eventId,
            player_id=u.player_id, game_id=u.game_id).update(player_type=u.player_type)


def set_player_stats(pd, team, game, players, period):
    pgss = []
    for sid in pd: # I swear that's not a Crosby reference
        iid = int(sid.replace("ID", ""))
        if "skaterStats" in pd[sid]["stats"]:
            jp = pd[sid]["stats"]["skaterStats"]
            if iid not in players:
                player = ingest_player(jp)
                players[player.id] = player
            else:
                player = players[iid]
            #try:
            #    pgs = pbpmodels.PlayerGameStats.objects.get(player=player, game=game)
            #except:
            pgs = pbpmodels.PlayerGameStats()
            pgs.player = player
            pgs.game = game
            pgs.timeOnIce = "00:" + jp["timeOnIce"]
            pgs.assists = jp["assists"]
            pgs.goals = jp["goals"]
            pgs.shots = jp["shots"]
            pgs.hits = jp["hits"]
            pgs.powerPlayGoals = jp["powerPlayGoals"]
            pgs.powerPlayAssists = jp["powerPlayAssists"]
            pgs.penaltyMinutes = jp["penaltyMinutes"]
            pgs.faceOffWins = jp["faceOffWins"]
            pgs.faceoffTaken = jp["faceoffTaken"]
            pgs.takeaways = jp["takeaways"]
            pgs.giveaways = jp["giveaways"]
            pgs.shortHandedGoals = jp["shortHandedGoals"]
            pgs.shortHandedAssists = jp["shortHandedAssists"]
            pgs.blocked = jp["blocked"]
            pgs.plusMinus = jp["plusMinus"]
            pgs.evenTimeOnIce = "00:" + jp["evenTimeOnIce"]
            pgs.powerPlayTimeOnIce = "00:" + jp["powerPlayTimeOnIce"]
            pgs.shortHandedTimeOnIce = "00:" + jp["shortHandedTimeOnIce"]
            pgs.period = period
            pgss.append(pgs)
    return pgss


def get_shifts(gid):
    # Get timecodes
    # For the diff between timecode and timecode after it
    #   Look for paths that start with /liveData/boxscore/teams/{{ home/away }}/onIce/
    #   Record those changes based on time from previously found
    pass


def get_woi_players():
    tplayers = pmodels.Player.objects.all()
    players = {}
    for t in tplayers:
        players[str(t.fullName)] = t.id
    convert = {}
    first = True
    for line in open("../../../data/roster.unique.csv"):
        if first is False:
            line = line.split(",")
            name = line[5].replace("\"", "").strip()
            woiid = line[8].replace("\"", "").strip()
            if name in players:
                convert[str(woiid)] = players[name]
            else:
                print name
        else:
            first = False
    return convert



def ingest_pbp_old():
    woi = get_woi_players()
    playtypes = set()
    playtext = set()
    types = set()
    types2 = set()
    games = pbpmodels.Game.objects.all().order_by("gamePk")
    count = 0
    play_convert = {"TAKE": "TAKEAWAY",
        "SOC": "SHOOTOUT_COMPLETE",
        "HIT": "HIT", "ICING": "STOP", "GIVE": "GIVEAWAY",
        "MISS": "MISSED_SHOT", "STOP": "STOP", "PEND": "PENALTY_END",
        "BLOCK": "BLOCKED_SHOT", "FAC": "FACEOFF", "PENL": "PENALTY",
        "SHOT": "SHOT", "OFFSIDE": "STOP"}
    playcount = 0
    for game in games:
        count += 1
        print count, len(games)
        existing = pbpmodels.PlayByPlay.objects.values("gamePk").filter(gamePk=game.gamePk)
        jpbp = None
        if len(existing) == 0:
            gcode = int(str(game.gamePk)[5:])
            files = glob.glob("../../../data/games" + str(game.season) + "*.json")
            for fp in files:
                begend = fp.replace("../../../data/games" + str(game.season) + "_", "").replace(".json", "").split("_")
                begend = [int(x) for x in begend]
                if gcode >= begend[0] and gcode <= begend[1]:
                    fp = open(fp)
                    j = json.load(fp)
                    for jg in j:
                        first = jg[0]
                        if int(first["season"]) == game.season and int(first["gcode"]) == gcode:
                            jpbp = jg
                            break
                    fp.close()
                    if jpbp is not None:
                        break
            if jpbp is not None:
                plays = []
                pois = []
                missing = 0
                for entry in jpbp:
                    play = pbpmodels.PlayByPlay()
                    play.id = playcount
                    playcount += 1
                    play.gamePk_id = game.gamePk
                    play.gameState = 3
                    play.period = entry["period"]
                    play.periodTime = "00:" + get_period_time(entry["seconds"])
                    play.homeScore = entry["home.score"]
                    play.awayScore = entry["away.score"]
                    if entry["etype"] in play_convert:
                        play.playType = play_convert[entry["etype"]]
                        play.playDescription = entry["etext"]
                        if play.playType == "SHOT":
                            play.shotType = entry["type"]
                            if entry["etext"] is not None and entry["type2"] is not None:
                                play.playDescription = entry["etext"] + " | " + entry["type2"]
                            elif entry["etext"] is not None:
                                play.playDescription = entry["etext"]
                            elif entry["type2"] is not None:
                                play.playDescription = entry["type2"]
                        elif play.playType == "PENALTY":
                            play.penaltySeverity = entry["type"]
                            play.penaltyMinutes = int(entry["type"][entry["type"].find("(")+1:entry["type"].find(")")].replace(" min", "").replace(" maj", "").replace("maj", "5"))
                    play.xcoord = entry["xcoord"]
                    play.ycoord = entry["ycoord"]
                    play.timeOnIce = entry["event.length"]
                    plays.append(play)
                    for ap in ["a1", "a2", "a3", "a4", "a5", "a6",
                                "h1", "h2", "h3", "h4", "h5", "h6"]:
                        poi = getPOI(playcount, game, entry, ap, woi)
                        if poi is not None:
                            pois.append(poi)
                        else:
                            missing += 1
                print len(pois), missing
                #pbpmodels.PlayByPlay.objects.bulk_create(plays)
                #pbpmodels.PlayerOnIce.objects.bulk_create(pois)


def getPOI(playcount, game, play, ap, woi):
    if play[ap] is not None:
        poi = pbpmodels.PlayerOnIce()
        poi.play_id = playcount
        poi.game = game
        if str(play[ap]) in woi:
            poi.player_id = woi[play[ap]]
        else:
            return None
        if play["etype"] == "FAC":
            if play["ev.player.1"] == play[ap]:
                poi.player_type = 1
            elif play["ev.player.2"] == play[ap]:
                poi.player_type = 2
        elif play["etype"] == "HIT":
            if play["ev.player.1"] == play[ap]:
                poi.player_type = 3
            elif play["ev.player.2"] == play[ap]:
                poi.player_type = 4
        elif play["etype"] == "SHOT":
            if play["ev.player.1"] == play[ap]:
                poi.player_type = 7
        elif play["etype"] == "BLOCK":
            if play["ev.player.1"] == play[ap]:
                poi.player_type = 7
            elif play["ev.player.2"] == play[ap]:
                poi.player_type = 9
        elif play["etype"] == "MISS":
            if play["ev.player.1"] == play[ap]:
                poi.player_type = 7
        elif play["etype"] == "GOAL":
            if play["ev.player.1"] == play[ap]:
                poi.player_type = 5
            elif play["ev.player.2"] == play[ap]:
                poi.player_type = 6
            elif play["ev.player.3"] == play[ap]:
                poi.player_type = 16
        elif play["etype"] == "PENL":
            if play["ev.player.1"] == play[ap]:
                poi.player_type = 10
            elif play["ev.player.2"] == play[ap]:
                poi.player_type = 11
        if poi.player_type is None:
            poi.player_type = 15
        return poi


    return None



def get_period_time(seconds):
    ps = 0
    period = "1st"
    if seconds <= 1200:
        ps = seconds
        period = "1st"
    elif seconds > 1200 and seconds <= 2400:
        ps = seconds - 1200
        period = "2nd"
    elif seconds > 2400 and seconds <= 3600:
        ps = seconds - 2400
        period = "3rd"
    else:
        ps = seconds - 3600
        period = "OT"
    minutes, seconds = divmod(ps, 60)
    seconds = str(seconds)
    minutes = str(minutes)
    if len(seconds) == 1:
        seconds = "0" + seconds
    if len(minutes) == 1:
        minutes = "0" + minutes
    return str(minutes) + ":" + str(seconds)




def ingest_games():
    season = 20162017
    tgames = set(pbpmodels.Game.objects.values_list("gamePk", flat=True).all())
    for team in tmodels.Team.objects.all():
        tid = team.id
        #egames = get_games(tid, str(season), egames=tgames)
        egames = get_playoff_games(tid, str(season), egames=tgames)


def get_games(tid, season, egames=set()):
    result = json.loads(api_calls.get_schedule(tid, season))
    games = []
    if "dates" in result:
        for jgames in result["dates"]:
            for jgame in jgames["games"]:
                if jgame["gamePk"] not in egames:
                    egames.add(jgame["gamePk"])
                    game = pbpmodels.Game()
                    game.gamePk = jgame["gamePk"]
                    game.link = jgame["link"]
                    game.gameType = jgame["gameType"]
                    game.season = jgame["season"]
                    game.dateTime = jgame["gameDate"]
                    game.awayTeam_id = jgame["teams"]["away"]["team"]["id"]
                    game.homeTeam_id = jgame["teams"]["home"]["team"]["id"]
                    try:
                        game.venue = tmodels.Venue.objects.get(name=jgame["venue"]["name"])
                    except:
                        venue = tmodels.Venue()
                        venue.name = jgame["venue"]["name"]
                        venue.save()
                        game.venue = venue
                    game.homeScore = jgame["teams"]["home"]["score"]
                    game.awayScore = jgame["teams"]["away"]["score"]
                    game.gameState = jgame["status"]["statusCode"]
                    games.append(game)
    pbpmodels.Game.objects.bulk_create(games)
    return egames


def get_playoff_games(season):
    result = json.loads(api_calls.get_schedule(season, "P"))
    if "dates" in result:
        for jgames in result["dates"]:
            for jgame in jgames["games"]:
                if jgame["status"]["statusCode"] != 8:
                    try:
                        venue = tmodels.Venue.objects.get(name=jgame["venue"]["name"])
                    except:
                        venue = tmodels.Venue()
                        venue.name = jgame["venue"]["name"]
                        venue.save()
                    awayTeam = tmodels.Team.objects.get(id=jgame["teams"]["away"]["team"]["id"])
                    homeTeam = tmodels.Team.objects.get(id=jgame["teams"]["home"]["team"]["id"])
                    game, created = pbpmodels.Game.objects.get_or_create(gamePk=jgame["gamePk"], season=season,
                        awayTeam=awayTeam, homeTeam=homeTeam, venue=venue)
                    game.link = jgame["link"]
                    game.gameType = jgame["gameType"]
                    game.season = jgame["season"]
                    game.dateTime = jgame["gameDate"]
                    game.homeScore = jgame["teams"]["home"]["score"]
                    game.awayScore = jgame["teams"]["away"]["score"]
                    game.gameState = jgame["status"]["statusCode"]
                    print game.dateTime
                    game.save()


def ingest_players():
    # For each team, get the roster
    team_rosters = {}
    for team in tmodels.Team.objects.all():
        team_rosters[team.id] = set()
        try:
            api = json.loads(api_calls.get_team_roster(team.id))
            for player in api["roster"]:
                team_rosters[team.id].add(player["person"]["id"])
        except:
            pass
    for team in team_rosters:
        print team
        try:
            jplayers = json.loads(api_calls.get_player(ids=team_rosters[team]))["people"]
            for jinfo in jplayers:
                try:
                    player = pmodels.Player.objects.get(id=jinfo["id"])
                except:
                    player = None
                print jinfo["fullName"]
                ingest_player(jinfo, team, player)
        except:
            pass


def ingest_player(jinfo, team=None, player=None):
    try:
        if player is None:
            player = pmodels.Player()
        player.id = jinfo["id"]
        player.fullName = jinfo["fullName"]
        player.link = jinfo["link"]
        player.firstName = jinfo["firstName"]
        player.lastName = jinfo["lastName"]
        if "primaryNumber" in jinfo:
            player.primaryNumber = jinfo["primaryNumber"]
        player.primaryPositionCode = jinfo["primaryPosition"]["code"]
        player.birthDate = jinfo["birthDate"]
        player.birthCity = jinfo["birthCity"]
        player.birthCountry = jinfo["birthCountry"]
        player.height = jinfo["height"]
        player.weight = jinfo["weight"]
        player.active = jinfo["active"]
        player.rookie = jinfo["rookie"]
        if "shootsCatches" in jinfo:
            player.shootsCatches = jinfo["shootsCatches"]
        if team is not None:
            player.currentTeam_id = team
        else:
            try:
                player.currentTeam = tmodels.Team.objects.get(id=jinfo["currentTeam"]["id"])
            except:
                pass
        player.rosterStatus = jinfo["rosterStatus"]
        player.save()
        return player
    except Exception as e:
        print e
        print jinfo



def ingest_teams():
    teams = api_calls.get_teams()
    teams = json.loads(teams)
    for jteam in teams["teams"]:
        team = tmodels.Team()
        team.id = jteam["id"]
        team.name = jteam["name"]
        team.shortName = jteam["shortName"]
        team.link = jteam["link"]
        team.abbreviation = jteam["abbreviation"]
        team.teamName = jteam["teamName"]
        team.locationName = jteam["locationName"]
        team.firstYearOfPlay = jteam["firstYearOfPlay"]
        team.conference = jteam["conference"]["name"][0]
        team.division = jteam["division"]["name"][0]
        team.officialSiteUrl = jteam["officialSiteUrl"]
        team.active = jteam["active"]

        venue = tmodels.Venue()
        venue.name = jteam["venue"]["name"]
        venue.city = jteam["venue"]["city"]
        venue.timeZone = jteam["venue"]["timeZone"]["id"]
        venue.timeZoneOffset = jteam["venue"]["timeZone"]["offset"]
        venue.save()

        team.venue = venue
        team.save()


if __name__ == "__main__":
    #ingest_games()
    #games = set(pbpmodels.Game.objects.values_list("gamePk", flat=True).filter(season=20162017))
    #badgames = pbpmodels.Game.objects.filter(season=20162017, gameType="P", gameState=8).delete()
    get_playoff_games("20162017")  #, games)
