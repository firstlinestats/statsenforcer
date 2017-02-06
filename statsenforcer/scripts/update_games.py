import os
import sys
import pytz
import json
import glob
import time
import django
from bs4 import BeautifulSoup

import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), "statsenforcer"))
sys.path.append("../")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "statsenforcer.settings")
from django.conf import settings

django.setup()

import team.models as tmodels
import player.models as pmodels
import playbyplay.models as pbpmodels
from django.db import transaction
import gzip

from StringIO import StringIO

from urllib2 import Request, urlopen, URLError

from compile_game_stats import compile_info
import api_calls

import fancystats
import sendemail
from get_media import game_media

headers = {
    "User-Agent" : "Mozilla/5.0 (X11; U; Linux i686; " + \
        "en-US; rv:1.9.2.24) Gecko/20111107 " + \
        "Linux Mint/9 (Isadora) Firefox/3.6.24",
}

BASE = "http://www.nhl.com/scores/htmlreports/"  # Base URL for html reports


def getPlayer(playerDict, number2name, currnum, backup_names, away):
    currnum = str(currnum)
    if away is False:
        if str(currnum) + "H" in backup_names:
            sn = backup_names[str(currnum) + "H"].upper().split(" ")
        else:
            sn = backup_names[str(currnum)].upper().split(" ")
    else:
        sn = backup_names[str(currnum)].upper().split(" ")
    # check for first name?
    for name in playerDict:
        ps = name.upper().split(" ")
        if len(ps) == len(sn):
            fp = ps[0]
            sp = sn[0]
            if (fp in sp or sp in fp) and ps[1] == sn[1]:
                return playerDict[name]
    # check for last name? seriously NHL?
    for name in playerDict:
        ps = name.upper().split(" ")
        if len(ps) == len(sn):
            fp = ps[-1]
            sp = sn[-1]
            if fp == sp:
                return playerDict[name]
    # check for player who didn't even play in that game, really NHL???
    try:
        if currnum in number2name:
            player = pmodels.Player.objects.get(fullName__iexact=number2name[currnum])
        else:
            player = pmodels.Player.objects.get(fullName__iexact=" ".join(sn))
        return player.id
    except Exception as e:
        print e
    print number2name[currnum], currnum, playerDict
    raise Exception


def checkGoalies(players, gamePk, team, period):
    goalies = []
    for player in players:
        playerstats = players[player]["stats"]
        if "goalieStats" in playerstats:
            gs = playerstats["goalieStats"]
            goalie = pbpmodels.GoalieGameStats()
            try:
                goalie.player = pmodels.Player.objects.get(id=player.replace("ID", ""))
            except:
                gplayer = ingest_player(json.loads(api_calls.get_player(player.replace("ID", "")))["people"][0])
                goalie.player = gplayer
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
            if "powerPlaySaves" in gs:
                goalie.powerPlaySaves = gs["powerPlaySaves"]
            else:
                goalie.powerPlaySaves = 0
            if "shortHandedSaves" in gs:
                goalie.shortHandedSaves = gs["shortHandedSaves"]
            else:
                goalie.shortHandedSaves = 0
            if "shortHandedShotsAgainst" in gs:
                goalie.shortHandedShotsAgainst = gs["shortHandedShotsAgainst"]
            else:
                goalie.shortHandedShotsAgainst = 0
            if "evenShotsAgainst" in gs:
                goalie.evenShotsAgainst = gs["evenShotsAgainst"]
            else:
                goalie.evenShotsAgainst = 0
            if "evenSaves" in gs:
                goalie.evenSaves = gs["evenSaves"]
            else:
                goalie.evenSaves = 0
            if "powerPlayShotsAgainst" in gs:
                goalie.powerPlayShotsAgainst = gs["powerPlayShotsAgainst"]
            else:
                goalie.powerPlayShotsAgainst = 0
            if "decision" in gs:
                goalie.decision = gs["decision"]
            goalie.save()
            goalies.append(goalie)
    return goalies


def ingest_player(jinfo, team=None, player=None):
    try:
        if player is None:
            player = pmodels.Player()
        if "id" in jinfo:
            player.id = jinfo["id"]
        else:
            raise Exception
        if "fullName" in jinfo:
            player.fullName = jinfo["fullName"]
        if "link" in jinfo:
            player.link = jinfo["link"]
        if "firstName" in jinfo:
            player.firstName = jinfo["firstName"]
        if "lastName" in jinfo:
            player.lastName = jinfo["lastName"]
        if "primaryNumber" in jinfo:
            player.primaryNumber = jinfo["primaryNumber"]
        if "primaryPosition" in jinfo and "code" in jinfo["primaryPosition"]:
            player.primaryPositionCode = jinfo["primaryPosition"]["code"]
        if "birthDate" in jinfo:
            player.birthDate = jinfo["birthDate"]
        if "birthCity" in jinfo:
            player.birthCity = jinfo["birthCity"]
        if "birthCountry" in jinfo:
            player.birthCountry = jinfo["birthCountry"]
        if "height" in jinfo:
            player.height = jinfo["height"]
        if "weight" in jinfo:
            player.weight = jinfo["weight"]
        if "active" in jinfo:
            player.active = jinfo["active"]
        if "rookie" in jinfo:
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


def set_player_stats(pd, team, game, players, period):
    pgss = []
    for sid in pd: # I swear that's not a Crosby reference
        iid = int(sid.replace("ID", ""))
        if "skaterStats" in pd[sid]["stats"]:
            jp = pd[sid]["stats"]["skaterStats"]
            if iid not in players:
                player = ingest_player(json.loads(api_calls.get_player(sid.replace("ID", "")))["people"][0])
                players[player.id] = player
            else:
                temp = pmodels.Player.objects.get(id=iid)
                player = ingest_player(json.loads(api_calls.get_player(sid.replace("ID", "")))["people"][0], player=temp)
                players[player.id] = player
            pgs = pbpmodels.PlayerGameStats()
            pgs.player = player
            pgs.game = game
            pgs.timeOnIce = "00:" + jp["timeOnIce"]
            pgs.assists = jp["assists"]
            pgs.goals = jp["goals"]
            pgs.shots = jp["shots"]
            pgs.hits = jp["hits"]
            if "powerPlayGoals" in jp:
                pgs.powerPlayGoals = jp["powerPlayGoals"]
            else:
                pgs.powerPlayGoals = 0
            if "powerPlayAssists" in jp:
                pgs.powerPlayAssists = jp["powerPlayAssists"]
            else:
                pgs.powerPlayAssists = 0
            if "penaltyMinutes" in jp:
                pgs.penaltyMinutes = jp["penaltyMinutes"]
            else:
                pgs.penaltyMinutes = 0
            if "faceOffWins" in jp:
                pgs.faceOffWins = jp["faceOffWins"]
            else:
                pgs.faceOffWins = 0
            if "faceoffTaken" in jp:
                pgs.faceoffTaken = jp["faceoffTaken"]
            else:
                pgs.faceoffTaken = 0
            if "takeaways" in jp:
                pgs.takeaways = jp["takeaways"]
            else:
                pgs.takeaways = 0
            if "giveaways" in jp:
                pgs.giveaways = jp["giveaways"]
            else:
                pgs.giveaways = 0
            if "shortHandedGoals" in jp:
                pgs.shortHandedGoals = jp["shortHandedGoals"]
            else:
                pgs.shortHandedGoals = 0
            if "shortHandedAssists" in jp:
                pgs.shortHandedAssists = jp["shortHandedAssists"]
            else:
                pgs.shortHandedAssists = 0
            pgs.blocked = jp["blocked"]
            pgs.plusMinus = jp["plusMinus"]
            if "evenTimeOnIce" in jp:
                pgs.evenTimeOnIce = "00:" + jp["evenTimeOnIce"]
            else:
                pgs.evenTimeOnIce = "00:00:00"
            if "powerPlayTimeOnIce" in jp:
                pgs.powerPlayTimeOnIce = "00:" + jp["powerPlayTimeOnIce"]
            else:
                pgs.powerPlayTimeOnIce = "00:00:00"
            if "shortHandedTimeOnIce" in jp:
                pgs.shortHandedTimeOnIce = "00:" + jp["shortHandedTimeOnIce"]
            else:
                pgs.shortHandedTimeOnIce = "00:00:00"
            pgs.period = period
            pgs.team = team
            pgss.append(pgs)
    return pgss


def find_current_games():
    today = datetime.datetime.now(tz=pytz.UTC)
    current_games = pbpmodels.Game.objects.exclude(gameState__in=[6,7,8,9]).filter(dateTime__lte=today, dateTime__gte=today - datetime.timedelta(7))
    return current_games


def find_past_games():
    today = datetime.datetime.now(tz=pytz.UTC)
    week_games = pbpmodels.Game.objects.filter(dateTime__lte=today, dateTime__gte=today - datetime.timedelta(7))
    return week_games


@transaction.atomic
def findStandings(season):

    j = json.loads(api_calls.get_standings())
    try:
        exists = tmodels.SeasonStats.objects.filter(date=datetime.date.today())
        exists.delete()
    except:
        pass
    for record in j["records"]:
        division = record["division"]["name"][0]
        conference = record["division"]["name"][0]
        for team in record["teamRecords"]:
            stat = tmodels.SeasonStats()
            stat.team_id = team["team"]["id"]
            stat.season = season
            try:
                stat.goalsAgainst = team["goalsAgainst"]
                stat.goalsScored = team["goalsScored"]
            except:
                pass
            stat.points = team["points"]
            stat.gamesPlayed = team["gamesPlayed"]
            stat.wins = team["leagueRecord"]["wins"]
            stat.losses = team["leagueRecord"]["losses"]
            stat.ot = team["leagueRecord"]["ot"]
            stat.date = datetime.date.today()
            try:
                stat.streakCode = team["streak"]["streakCode"]
            except:
                pass
            try:
                stat.save()
            except:
                pass


@transaction.atomic()
def update_game(game, players):
    missing_players = set()
    allpgss = []
    allperiods = []
    allplaybyplay = []
    allplayers = []
    homeMissed = 0
    awayMissed = 0
    # Delete old data
    if pbpmodels.GamePeriod.objects.filter(game=game).count() > 0:
        pbpmodels.GamePeriod.objects.filter(game=game).delete()
    if pbpmodels.PlayerInPlay.objects.filter(game=game).count() > 0:
        pbpmodels.PlayerInPlay.objects.filter(game=game).delete()
    if pbpmodels.PlayByPlay.objects.filter(gamePk=game).count() > 0:
        pbpmodels.PlayByPlay.objects.filter(gamePk=game).delete()
    if pbpmodels.PlayerGameStats.objects.filter(game=game).count() > 0:
        pbpmodels.PlayerGameStats.objects.filter(game=game).delete()
    # Get live game data
    j = json.loads(api_calls.get_game(game.gamePk))
    gd = j["gameData"]
    ld = j["liveData"]
    boxScore = ld["boxscore"]
    lineScore = ld["linescore"]
    # Update gameData
    game.dateTime = gd["datetime"]["dateTime"]
    if "endDateTime" in gd["datetime"]:
        game.endDateTime = gd["datetime"]["endDateTime"]
    game.gameState = gd["status"]["codedGameState"]
    # Get linescore information
    game.homeScore = lineScore["teams"]["home"]["goals"]
    game.awayScore = lineScore["teams"]["away"]["goals"]
    game.homeShots = lineScore["teams"]["home"]["shotsOnGoal"]
    game.awayShots = lineScore["teams"]["away"]["shotsOnGoal"]
    # Get boxscore information
    home = boxScore["teams"]["home"]["teamStats"]["teamSkaterStats"]
    away = boxScore["teams"]["away"]["teamStats"]["teamSkaterStats"]
    game.homePIM = home["pim"]
    game.awayPIM = away["pim"]
    game.homePPGoals = home["powerPlayGoals"]
    game.awayPPGoals = away["powerPlayGoals"]
    game.homePPOpportunities = home["powerPlayOpportunities"]
    game.awayPPOpportunities = away["powerPlayOpportunities"]
    game.homeFaceoffPercentage = home["faceOffWinPercentage"]
    game.awayFaceoffPercentage = away["faceOffWinPercentage"]
    game.homeBlocked = home["blocked"]
    game.awayBlocked = away["blocked"]
    game.homeTakeaways = home["takeaways"]
    game.awayTakeaways = away["takeaways"]
    game.homeGiveaways = home["giveaways"]
    game.awayGiveaways = away["giveaways"]
    game.homeHits = home["hits"]
    game.awayHits = away["hits"]
    cperiod = 1
    for period in lineScore["periods"]:
        p = pbpmodels.GamePeriod()
        p.game = game
        p.period = period["num"]
        if period["num"] > cperiod:
            cperiod = period["num"]
        if "startTime" in period:
            p.startTime = period["startTime"]
        if "endTime" in period:
            p.endTime = period["endTime"]
        p.homeScore = period["home"]["goals"]
        p.homeShots = period["home"]["shotsOnGoal"]
        p.awayScore = period["away"]["goals"]
        p.awayShots = period["away"]["shotsOnGoal"]
        allperiods.append(p)
    if lineScore["hasShootout"]:
        sinfo = lineScore["shootoutInfo"]
        try:
            s = pbpmodels.Shootout.objects.get(game=game)
        except:
            s = pbpmodels.Shootout()
            s.game = game
        s.awayScores = sinfo["away"]["scores"]
        s.awayAttempts = sinfo["away"]["attempts"]
        s.homeScores = sinfo["home"]["scores"]
        s.homeAttempts = sinfo["home"]["attempts"]
        s.save()
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
    playid = pbpmodels.PlayByPlay.objects.values('id').latest('id')['id'] + 1
    homeScore = 0
    awayScore = 0
    for play in ld["plays"]["allPlays"]:
        about = play["about"]
        if "players" in play:
            pplayers = play["players"]
        else:
            pplayers = {}
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
        if "x" in coordinates and "y" in coordinates:
            p.xcoord = coordinates["x"]
            p.ycoord = coordinates["y"]
        if result["eventTypeId"] == "GOAL":
            if play["team"]["id"] == game.homeTeam_id:
                homeScore += 1
            else:
                awayScore += 1
        p.homeScore = homeScore
        p.awayScore = awayScore
        allplaybyplay.append(p)
        assist_found = False
        for pp in pplayers:
            skip_play = False  # For all those preseason players that don't exist!
            poi = pbpmodels.PlayerInPlay()
            poi.play_id = playid
            poi.game = game
            try:
                playerfound = pmodels.Player.objects.get(id=pp["player"]["id"])
            except:
                try:
                    if pp["player"]["id"] not in missing_players:
                        playerdata = json.loads(api_calls.get_player(pp["player"]["id"]))
                        if len(playerdata.keys()) > 0:
                            playerfound = ingest_player(playerdata)
                        else:
                            skip_play = True
                            missing_players.add(pp["player"]["id"])
                    else:
                        skip_play = True
                except:
                    skip_play = True
                    missing_players.add(pp["player"]["id"])
            poi.player_id = pp["player"]["id"]
            if assist_found is True and fancystats.player.get_player_type(pp["playerType"]) == 6:
                poi.player_type = 16
                poi.eventId = about["eventId"]
                poi.game_id = game.gamePk
            else:
                poi.player_type = fancystats.player.get_player_type(pp["playerType"])
                if poi.player_type == 6:
                    assist_found = True
            if skip_play is False:
                allplayers.append(poi)
        playid += 1
    game.homeMissed = homeMissed
    game.awayMissed = awayMissed
    game.save()
    pbpmodels.GamePeriod.objects.bulk_create(allperiods)
    pbpmodels.PlayByPlay.objects.bulk_create(allplaybyplay)
    pbpmodels.PlayerInPlay.objects.bulk_create(allplayers)
    hp = boxScore["teams"]["home"]["players"]
    ap = boxScore["teams"]["away"]["players"]
    homegoalies = ld["boxscore"]["teams"]["home"]["players"]
    awaygoalies = ld["boxscore"]["teams"]["away"]["players"]
    hometeam = ld["boxscore"]["teams"]["home"]["team"]["id"]
    awayteam = ld["boxscore"]["teams"]["away"]["team"]["id"]
    goaliestats = []
    goaliestats.extend(checkGoalies(homegoalies, game.gamePk, hometeam, cperiod))
    goaliestats.extend(checkGoalies(awaygoalies, game.gamePk, awayteam, cperiod))
    allpgss.extend(set_player_stats(hp, game.homeTeam, game, players, cperiod))
    allpgss.extend(set_player_stats(ap, game.awayTeam, game, players, cperiod))
    pbpmodels.PlayerGameStats.objects.bulk_create(allpgss)

    # Find any existing POI data and delete
    pbpmodels.PlayerOnIce.objects.filter(game=game).delete()
    # Get player on ice data
    eventIdxs = {}
    for pbp in allplaybyplay:
        periodTime = str(pbp.periodTime)
        if pbp.period not in eventIdxs:
            eventIdxs[pbp.period] = {}
        if periodTime not in eventIdxs[pbp.period]:
            eventIdxs[pbp.period][periodTime] = {}
        if fancystats.constants.events[pbp.playType] not in eventIdxs[pbp.period][periodTime]:
            eventIdxs[pbp.period][periodTime][fancystats.constants.events[pbp.playType]] = [pbp.id, ]
        else:
            eventIdxs[pbp.period][periodTime][fancystats.constants.events[pbp.playType]].append(pbp.id)
    hp = {}
    ap = {}
    for ps in allpgss:
        if ps.team_id == game.homeTeam_id:
            hp[ps.player.fullName.upper()] = ps.player_id
        else:
            ap[ps.player.fullName.upper()] = ps.player_id
    for gs in goaliestats:
        if gs.team_id == game.homeTeam_id:
            hp[gs.player.fullName.upper()] = gs.player_id
        else:
            ap[gs.player.fullName.upper()] = gs.player_id
    url = BASE + str(game.season) + "/PL0" + str(game.gamePk)[5:] + ".HTM"
    data = api_calls.get_url(url)
    soup = BeautifulSoup(data, 'html.parser')
    evens = soup.find_all('tr', attrs={'class': 'evenColor'})
    count = 0
    saved = []
    for row in evens:
        backup_names = {}
        cols = row.find_all('td', recursive=False)
        fonts = row.find_all('font')
        if len(list(cols[3].strings)) >= 1:
            time = list(cols[3].strings)[0]
            if len(time) < 5:
                time = "0" + time
            for ele in fonts:
                if ele.has_attr("title"):
                    title = ele.attrs["title"].split(" - ")[1]
                    number = ele.text
                    if number in backup_names:
                        backup_names[number + "H"] = title
                    else:
                        backup_names[number] = title
            fcols = [ele.text.strip().replace("\n", "") for ele in cols]
            eventIdx = int(fcols[1])
            playType = fcols[4]
            if eventIdx in eventIdxs and time in eventIdxs[eventIdx] and playType in eventIdxs[eventIdx][time]:
                players = fcols[6:]
                away = players[0]
                home = players[1]
                away = [x[0:-1] for x in away.replace(u'\xa0', " ").split(" ")]
                home = [x[0:-1] for x in home.replace(u'\xa0', " ").split(" ")]
                awayNames = {}
                homeNames = {}
                for f in fonts:
                    if "title" in f:
                        title = f["title"].split(" - ")[-1]
                        number = f.text
                        if number in away and number not in awayNames:
                            awayNames[number] = title
                        else:
                            homeNames[number] = title
                acount = 1
                players = set()
                for anum in away:
                    if len(anum) > 0:
                        for play_id in eventIdxs[eventIdx][time][playType]:
                            pbpdict = {}
                            pbpdict["play_id"] = play_id
                            pbpdict["game_id"] = game.gamePk
                            anum = int(anum)
                            try:
                                player = getPlayer(ap, awayNames, anum, backup_names, True) #ap[awayNames[str(anum)]]
                                if player not in players:
                                    players.add(player)
                                    pbpdict["player_id"] = player
                                    acount += 1
                                    pbpp = pbpmodels.PlayerOnIce(**pbpdict)
                                    #pbpp.save()
                                    saved.append(pbpp)
                            except:
                                pass
                hcount = 1
                for hnum in home:
                    if len(hnum) > 0:
                        for play_id in eventIdxs[eventIdx][time][playType]:
                            pbpdict = {}
                            pbpdict["play_id"] = play_id
                            pbpdict["game_id"] = game.gamePk
                            # fix yo formatting nhl dot com
                            hnum = int(str(hnum).replace("=\"center\">", "").replace("C", ""))
                            try:
                                player = getPlayer(hp, homeNames, hnum, backup_names, False)
                                if player not in players:
                                    players.add(player)
                                    pbpdict["player_id"] = player
                                    hcount += 1
                                    pbpp = pbpmodels.PlayerOnIce(**pbpdict)
                                    #pbpp.save()
                                    saved.append(pbpp)
                            except:
                                pass
                # Remove so there are no duplicates, first entry will have the most data
                eventIdxs[eventIdx][time].pop(playType, None)
    pbpmodels.PlayerOnIce.objects.bulk_create(saved)
    if game.gameState in [6,7,8,"6","7","8"]:
        return True
    return False


def main():
    # Find games that are current
    current_games = find_current_games()
    todaycheck = None
    # set a test for an instance where we don't want to keep running?
    keep_running = True
    players = {}
    tplayers = pmodels.Player.objects.all()
    for t in tplayers:
        players[t.id] = t
    # Loop through current games
    emailssent = 0
    while keep_running:
        # Loop through current_games
        for game in current_games:
            try:
                # Call function that will handle most of the work, return True if the game has finished
                finished = update_game(game, players)
                try:
                    game_media(game.gamePk)
                except:
                    # no media, yet...
                    pass
                # If the game has finished, compile the final stats
                if finished:
                    fgame = {"gamePk": game.gamePk, "homeTeam_id": game.homeTeam_id,
                        "awayTeam_id": game.awayTeam_id}
                    # Delete any existing
                    with transaction.atomic():
                        compile_info(game.gamePk)
                        findStandings(game.season)
            except Exception as e:
                sendemail.send_error_email("Exception: {}, Game: {}, ".format(e, game.gamePk))
                emailssent += 1
                if emailssent > 5:
                    raise Exception("Issue running. Please debug and restart...")
        #return
        # Find active games and loop back up, repeating
        current_games = find_current_games()
        if len(current_games) == 0:
            emailssent = 0
            gameTime = pbpmodels.Game.objects.filter(gameState=1).earliest("dateTime").dateTime
            today = datetime.datetime.now(tz=pytz.UTC)
            diff = gameTime - today
            seconds = diff.total_seconds() - 60
            datecheck = datetime.datetime.today()
            skip_initial = False
            if todaycheck is not None:
                diff = datecheck - todaycheck
                diff = diff.total_seconds()
            else:
                diff = 12 * 60 * 60 + 1  # Force an initial email
            # If it's been at least 12 hours since last email, check to see if anymore games today
            if diff > 12 * 60 * 60 and seconds > 4 * 60 * 60:
                # Run daily email check and make sure any corrections from past week are looked at
                if todaycheck is None:
                    startday = datecheck - datetime.timedelta(hours=12)
                else:
                    startday = todaycheck
                todaysgames = pbpmodels.Game.objects.filter(dateTime__gte=startday, dateTime__lte=datecheck)
                if len(todaysgames) > 0:
                    sendemail.send_update_email(todaysgames)
                    check_rosters()
                    current_games = pbpmodels.Game.objects.filter(dateTime__gte=datecheck-datetime.timedelta(7), dateTime__lte=datecheck)
                    todaycheck = datecheck
                    skip_initial = True
            if seconds > 0 and not skip_initial:
                time.sleep(seconds)
            else:
                time.sleep(60)
        else:
            # sleep for one minute
            time.sleep(60)


def test():
    datecheck = datetime.datetime.today()
    startday = datecheck - datetime.timedelta(1.5)
    todaysgames = pbpmodels.Game.objects.filter(dateTime__gte=startday, dateTime__lte=datecheck)
    sendemail.send_update_email(todaysgames)


def fix_missing():
    players = {}
    tplayers = pmodels.Player.objects.all()
    for t in tplayers:
        players[t.id] = t
    existing = set(pbpmodels.PlayByPlay.objects.values_list("gamePk_id", flat=True).all())
    missing = pbpmodels.Game.objects.exclude(gamePk__in=existing).filter(gamePk__gte=2016020001)
    for game in missing:
        print game.gamePk
        finished = update_game(game, players)


def get_players():
    players = {}
    tplayers = pmodels.Player.objects.all()
    for t in tplayers:
        players[t.id] = t
    return players


def reset_game(gamePk, players=None):
    if not players:
        players = {}
        tplayers = pmodels.Player.objects.all()
        for t in tplayers:
            players[t.id] = t
    game = pbpmodels.Game.objects.get(gamePk=gamePk)
    update_game(game, players)
    compile_info(gamePk)


def check_rosters():
    teamids = tmodels.Team.objects.values_list("id", flat=True).filter(active=True)
    rdata = api_calls.get_team_rosters([str(x) for x in teamids])
    rdata = json.loads(rdata)
    for team in rdata["teams"]:
        roster = pmodels.Player.objects.filter(currentTeam_id=team["id"])
        cplayers = {}
        for player in team["roster"]["roster"]:
            cplayers[player["person"]["id"]] = player["person"]["rosterStatus"]
        for player in roster:
            if player.id not in cplayers:
                player.currentTeam = None
                player.save()
            else:
                if cplayers[player.id] != player.rosterStatus:
                    player.rosterStatus = cplayers[player.id]
                    player.save()
                cplayers.pop(player.id, None)
        print "{} new players for {}".format(len(cplayers), team["teamName"])
        for pid in cplayers:
            print pid
            try:
                newplayer = pmodels.Player.objects.get(id=pid)
                newplayer.currentTeam_id = team["id"]
                newplayer.save()
            except:
                newplayer = ingest_player(json.loads(api_calls.get_player(pid))["people"][0])
                newplayer.save()


def reset_games():
    game_list = [2015020994, 2015021001, 2015021018, 2015021021]
    players = get_players()
    for game in game_list:
        print "Fixing {}...".format(game)
        reset_game(game)


if __name__ == "__main__":
    #reset_game(2015020961)
    #reset_games()
    try:
        main()
    except:
        sendemail.send_error_email("Too many issues, cancelling...")
    #check_rosters()
    #fix_missing()
