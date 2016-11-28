from django.shortcuts import render, get_object_or_404
from django.http import Http404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from team.models import Team
from player.models import Player, PlayerGameFilterStats
from datetime import date, datetime
from playbyplay.forms import GameForm

import playerqueries

from fancystats import toi, corsi


def players(request):
    teamstrength = "all"
    scoresituation = "all"
    period = "all"
    form = GameForm()
    if request.method == 'GET':
        form = GameForm(request.GET)
        if form.is_valid():
            cd = form.cleaned_data
            teamstrength = cd["teamstrengths"]
            scoresituation = cd["scoresituation"]
            period = cd["period"]
    pgs = PlayerGameFilterStats.objects.raw(playerqueries.playersquery, [scoresituation, teamstrength, period])

    stats = {}
    for row in pgs:
        season = row.season
        playerid = row.player_id
        if playerid not in stats:
            stats[playerid] = {}
        if season not in stats[playerid]:
            stats[playerid][season] = row.__dict__
            stats[playerid][season]["games"] = 1
            stats[playerid][season].pop("_state", None)
            stats[playerid][season].pop("game_id", None)
            stats[playerid][season].pop("period", None)
            stats[playerid][season].pop("teamstrength", None)
            stats[playerid][season].pop("scoresituation", None)
            stats[playerid][season].pop("player_id", None)
        else:
            stats[playerid][season]["games"] += 1
            for key in stats[playerid][season]:
                if key not in ["abbreviation", "teamName", "shortName", "fullName"]:
                    try:
                        stats[playerid][season][key] += row.__dict__[key]
                    except:
                        pass
                elif key == "abbreviation":
                    if stats[playerid][season][key] != row.__dict__[key]:
                        stats[playerid][season][key] += u", {}".format(row.__dict__[key])
                elif key == "teamName":
                    if stats[playerid][season][key] != row.__dict__[key]:
                        stats[playerid][season][key] += u", {}".format(row.__dict__[key])
                elif key == "shortName":
                    if stats[playerid][season][key] != row.__dict__[key]:
                        stats[playerid][season][key] += u", {}".format(row.__dict__[key])
    for playerid in stats:
        for season in stats[playerid]:
            row = stats[playerid][season]
            row["toi"] = toi.format_minutes(row["toi"] / row["games"])
            row["fo"] = '%.2f' % corsi.corsi_percent(row["fo_w"], row["fo_l"])
            row["sf"] = '%.2f' % corsi.corsi_percent(row["shotsFor"], row["shotsAgainst"])
            row["msf"] = '%.2f' % corsi.corsi_percent(row["missedShotsFor"],
                row["missedShotsAgainst"])
            row["bsf"] = '%.2f' % corsi.corsi_percent(row["blockedShotsFor"],
                row["blockedShotsAgainst"])
            row["gf"] = '%.2f' % corsi.corsi_percent(row["goalsFor"], row["goalsAgainst"])
            row["cf"] = '%.2f' % corsi.corsi_percent(row["corsiFor"], row["corsiAgainst"])
            row["ff"] = '%.2f' % corsi.corsi_percent(row["fenwickFor"], row["fenwickAgainst"])
            row["hit"] = '%.2f' % corsi.corsi_percent(row["hitFor"], row["hitAgainst"])
            row["pn"] = '%.2f' % corsi.corsi_percent(row["penaltyFor"], row["penaltyAgainst"])
            row["scf"] = '%.2f' % corsi.corsi_percent(row["scoringChancesFor"], row["scoringChancesAgainst"])
            row["hscf"] = '%.2f' % corsi.corsi_percent(row["highDangerScoringChancesFor"], row["highDangerScoringChancesAgainst"])
            if row["neutralZoneStarts"] is not None:
                row["zso"] = '%.2f' % corsi.corsi_percent(row["offensiveZoneStarts"], row["neutralZoneStarts"] + row["defensiveZoneStarts"])
            else:
                row["zso"] = "0.0"

    context = {}
    context["form"] = form
    context["stats"] = stats
    return render(request, 'players/players.html', context)

def player_page(request, player_id):
    today = datetime.now()
    player = get_object_or_404(Player, pk=player_id)
    player.age = today.year - player.birthDate.year - ((today.month, today.day) < (player.birthDate.month, player.birthDate.day))
    teamstrength = "all"
    scoresituation = "all"
    period = "all"
    if request.method == "GET":
        form = GameForm(request.GET)
        if form.is_valid():
            cd = form.cleaned_data
            teamstrength = cd["teamstrengths"]
            scoresituation = cd["scoresituation"]
            period = cd["period"]
    pgs = PlayerGameFilterStats.objects.raw(playerqueries.playerquery, [scoresituation, teamstrength, period, player.id])
    stats = {}
    for row in pgs:
        season = row.season
        playerid = player.id
        if playerid not in stats:
            stats[playerid] = {}
        if season not in stats[playerid]:
            stats[playerid][season] = row.__dict__
            stats[playerid][season]["games"] = 1
            stats[playerid][season].pop("_state", None)
            stats[playerid][season].pop("game_id", None)
            stats[playerid][season].pop("period", None)
            stats[playerid][season].pop("teamstrength", None)
            stats[playerid][season].pop("scoresituation", None)
            stats[playerid][season].pop("player_id", None)
        else:
            stats[playerid][season]["games"] += 1
            for key in stats[playerid][season]:
                if key not in ["abbreviation", "teamName", "shortName"]:
                    try:
                        stats[playerid][season][key] += row.__dict__[key]
                    except:
                        pass
                elif key == "abbreviation":
                    if stats[playerid][season][key] != row.__dict__[key]:
                        stats[playerid][season][key] += ", {}".format(row.__dict__[key])
                elif key == "teamName":
                    if stats[playerid][season][key] != row.__dict__[key]:
                        stats[playerid][season][key] += ", {}".format(row.__dict__[key])
                elif key == "shortName":
                    if stats[playerid][season][key] != row.__dict__[key]:
                        stats[playerid][season][key] += ", {}".format(row.__dict__[key])
    for playerid in stats:
        for season in stats[playerid]:
            row = stats[playerid][season]
            row["toi"] = toi.format_minutes(row["toi"] / row["games"])
            row["fo"] = '%.2f' % corsi.corsi_percent(row["fo_w"], row["fo_l"])
            row["sf"] = '%.2f' % corsi.corsi_percent(row["shotsFor"], row["shotsAgainst"])
            row["msf"] = '%.2f' % corsi.corsi_percent(row["missedShotsFor"],
                row["missedShotsAgainst"])
            row["bsf"] = '%.2f' % corsi.corsi_percent(row["blockedShotsFor"],
                row["blockedShotsAgainst"])
            row["gf"] = '%.2f' % corsi.corsi_percent(row["goalsFor"], row["goalsAgainst"])
            row["cf"] = '%.2f' % corsi.corsi_percent(row["corsiFor"], row["corsiAgainst"])
            row["ff"] = '%.2f' % corsi.corsi_percent(row["fenwickFor"], row["fenwickAgainst"])
            row["hit"] = '%.2f' % corsi.corsi_percent(row["hitFor"], row["hitAgainst"])
            row["pn"] = '%.2f' % corsi.corsi_percent(row["penaltyFor"], row["penaltyAgainst"])
            row["scf"] = '%.2f' % corsi.corsi_percent(row["scoringChancesFor"], row["scoringChancesAgainst"])
            row["hscf"] = '%.2f' % corsi.corsi_percent(row["highDangerScoringChancesFor"], row["highDangerScoringChancesAgainst"])
            if row["neutralZoneStarts"] is not None:
                row["zso"] = '%.2f' % corsi.corsi_percent(row["offensiveZoneStarts"], row["neutralZoneStarts"] + row["defensiveZoneStarts"])
            else:
                row["zso"] = 0

    context = {}
    context["player"] = player
    context["form"] = form
    context["stats"] = stats
    return render(request, 'players/player_page.html', context)
