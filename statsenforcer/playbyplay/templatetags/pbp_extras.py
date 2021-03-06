from django import template

from fancystats import constants
from fancystats import player

import datetime
import pytz

register = template.Library()

local_tz = pytz.timezone('US/Eastern')


def utc_to_local(utc_dt):
    local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
    return local_tz.normalize(local_dt) # .normalize might be unnecessary


@register.filter
def fix_date(dateTime):
    return datetime.datetime.strftime(utc_to_local(dateTime), "%b %d, %I:%M %p %Z")


@register.filter
def fix_time(dateTime):
    return datetime.datetime.strftime(utc_to_local(dateTime), "%I:%M %p %Z")


def find_value(default, key, cd, CHOICES):
    if key in cd:
        for choice in CHOICES:
            if choice[0] == cd[key]:
                default = choice[1]
                break
    return default


@register.filter
def format_form_state(form):
    cd = form.cleaned_data
    teamstrengths = find_value("Even Strength 5v5", "teamstrengths", cd, constants.TEAMSTRENGTHS_CHOICES)
    scoringsituations = find_value("All Scoring Situations", "scoresituation", cd, constants.SCORESITUATION_CHOICES)
    period = find_value("All Periods", "period", cd, constants.PERIOD_CHOICES)
    if teamstrengths == "All":
        teamstrengths = "All Team Strengths"
    if scoringsituations == "All":
        scoringsituations = "All Scoring Situations"
    if period == "All":
        period = "All Periods"
    scoring = "{}".format(scoringsituations)
    periods = get_period(period)
    default = "{}, {}, {}".format(teamstrengths, scoring, periods)
    return default

@register.filter
def player_position(position):
    return player.get_player_position(position)


@register.filter
def get_item(dictionary, key):
    if dictionary is not None and key in dictionary:
        return dictionary.get(key)
    return ""


@register.filter
def get_period(period):
    try:
        period = int(period)
    except:
        return period
    if period == 1:
        periodTime = "1st Period"
    elif period == 2:
        periodTime = "2nd Period"
    elif period == 3:
        periodTime = "3rd Period"
    else:
        periodTime = "Overtime (" + str(period) + ")"
    return periodTime


@register.filter
def create_play_text(play):
    if play["playType"] == "GAME_SCHEDULED":
        return "Game has been scheduled"
    elif play["playType"] == "PERIOD_READY":
        return get_period(play["period"]) + " is ready"
    elif play["playType"] == "PERIOD_START":
        return get_period(play["period"]) + " has started"
    elif play["playType"] == "FACEOFF":
        winner = ""
        loser = ""
        for player in play["players"]:
            if player["player_type"] == 1:
                winner = "<b>" + player["player__fullNameTeam"] + "</b>"
            else:
                loser = "<b>" + player["player__fullNameTeam"] + "</b>"
        return winner + " won faceoff against " + loser
    elif play["playType"] == "HIT":
        hitter = ""
        hittee = ""
        for player in play["players"]:
            if player["player_type"] == 3:
                hitter = "<b>" + player["player__fullNameTeam"] + "</b>"
            else:
                hittee = "<b>" + player["player__fullNameTeam"] + "</b>"
        return hitter + " hit " + hittee
    elif play["playType"] == "SHOT":
        shooter = ""
        goalie = ""
        for player in play["players"]:
            if player["player_type"] == 7:
                shooter = "<b>" + player["player__fullNameTeam"] + "</b>"
            else:
                goalie = "<b>" + player["player__fullNameTeam"] + "</b>"
        return shooter + " shot, saved by " + goalie
    elif play["playType"] == "BLOCKED_SHOT":
        shooter = ""
        blocker = ""
        for player in play["players"]:
            if player["player_type"] == 7:
                shooter = "<b>" + player["player__fullNameTeam"] + "</b>"
            else:
                blocker = "<b>" + player["player__fullNameTeam"] + "</b>"
        return shooter + " shot, blocked by " + blocker
    elif play["playType"] == "MISSED_SHOT":
        shooter = ""
        for player in play["players"]:
            shooter = "<b>" + player["player__fullNameTeam"] + "</b>"
        return shooter + " shot, missed"
    elif play["playType"] == "GIVEAWAY":
        playername = ""
        for player in play["players"]:
            playername = "<b>" + player["player__fullNameTeam"] + "</b>"
        return playername + " giveaway"
    elif play["playType"] == "TAKEAWAY":
        playername = ""
        for player in play["players"]:
            playername = "<b>" + player["player__fullNameTeam"] + "</b>"
        return playername + " takeaway"
    elif play["playType"] == "STOP":
        return "Play stopped"
    elif play["playType"] == "PERIOD_END":
        return "Period has ended"
    elif play["playType"] == "PERIOD_OFFICIAL":
        return "Period has been marked as official"
    elif play["playType"] == "GOAL":
        shooter = ""
        assist1 = ""
        assist2 = ""
        for player in play["players"]:
            if player["player_type"] == 5:
                shooter = player["player__fullNameTeam"]
            elif player["player_type"] == 6:
                assist1 = player["player__fullNameTeam"]
            elif player["player_type"] == 16:
                assist2 = player["player__fullNameTeam"]
        info = "<b>{}</b> scored".format(shooter)
        if play["shotType"]:
            info += "({})".format(play["shotType"])
        if assist1 != "":
            info += ", assisted by <b>" + assist1 + "</b>"
        if assist2 != "":
            info += " and <b>" + assist2 + "</b>"
        return info
    elif play["playType"] == "PENALTY":
        return play["penaltySeverity"] + ": " + play["playDescription"] + " (" + str(play["penaltyMinutes"]) + " minutes)"
    elif play["playType"] == "CHALLENGE":
        return play["playDescription"]
    elif play["playType"] == "GAME_END":
        return "Game over."

    return ""
