from django import template

from fancystats import constants

register = template.Library()

@register.filter
def get_period(period):
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
                winner = player["player__fullName"]
            else:
                loser = player["player__fullName"]
        return winner + " won faceoff against " + loser
    elif play["playType"] == "HIT":
        hitter = ""
        hittee = ""
        for player in play["players"]:
            if player["player_type"] == 3:
                hitter = player["player__fullName"]
            else:
                hittee = player["player__fullName"]
        return hitter + " hit " + hittee
    elif play["playType"] == "SHOT":
        shooter = ""
        goalie = ""
        for player in play["players"]:
            if player["player_type"] == 7:
                shooter = player["player__fullName"]
            else:
                goalie = player["player__fullName"]
        return shooter + " shot, saved by " + goalie
    elif play["playType"] == "BLOCKED_SHOT":
        shooter = ""
        blocker = ""
        for player in play["players"]:
            if player["player_type"] == 7:
                shooter = player["player__fullName"]
            else:
                blocker = player["player__fullName"]
        return shooter + " shot, blocked by " + blocker
    elif play["playType"] == "MISSED_SHOT":
        shooter = ""
        for player in play["players"]:
            shooter = player["player__fullName"]
        return shooter + " shot, missed"
    elif play["playType"] == "GIVEAWAY":
        playername = ""
        for player in play["players"]:
            playername = player["player__fullName"]
        return playername + " giveaway"
    elif play["playType"] == "TAKEAWAY":
        playername = ""
        for player in play["players"]:
            playername = player["player__fullName"]
        return playername + " takeaway"
    elif play["playType"] == "STOP":
        return "Play stopped"
    elif play["playType"] == "PERIOD_END":
        return "Period has ended"
    elif play["playType"] == "PERIOD_OFFICIAL":
        return "Period has been marked as official"
    elif play["playType"] == "GOAL":
        print play
        shooter = ""
        assist1 = ""
        assist2 = ""
        for player in play["players"]:
            if player["player_type"] == 5:
                shooter = player["player__fullName"]
            elif player["player_type"] == 6:
                assist1 = player["player__fullName"]
            elif player["player_type"] == 16:
                assist2 = player["player__fullName"]
        info = shooter + " scored (" + play["shotType"] + ")"
        if assist1 != "":
            info += ", assisted by " + assist1
        if assist2 != "":
            info += ", and " + assist2
        return "<b>" + info + "</b>"
    else:
        print play["playType"]

    return ""
