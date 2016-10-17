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
        info = "<b>" + shooter + "</b> scored (" + play["shotType"] + ")"
        if assist1 != "":
            info += ", assisted by <b>" + assist1 + "</b>"
        if assist2 != "":
            info += " and <b>" + assist2 + "</b>"
        return info
    elif play["playType"] == "PENALTY":
        return play["penaltySeverity"] + ": " + play["playDescription"] + " (" + str(play["penaltyMinutes"]) + " minutes)"
    elif play["playType"] == "CHALLENGE":
        return play["playDescription"]
    else:
        print play["playType"]

    return ""
