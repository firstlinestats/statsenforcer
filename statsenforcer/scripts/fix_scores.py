import os
import sys
import django

sys.path.append(os.path.join(os.path.dirname(__file__), "statsenforcer"))
sys.path.append("../")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "statsenforcer.settings")
from django.conf import settings

django.setup()

import team.models as tmodels
import player.models as pmodels
import playbyplay.models as pbpmodels
from django.db import transaction


def main():
    homescored = pbpmodels.PlayByPlay.objects.values_list("gamePk_id", flat=True).filter(playType="GAME_SCHEDULED", homeScore__gte=1)
    awayscored = pbpmodels.PlayByPlay.objects.values_list("gamePk_id", flat=True).filter(playType="GAME_SCHEDULED", awayScore__gte=1)
    incorrect = set(homescored | awayscored)
    isize = len(incorrect)
    count = 0
    for game in incorrect:
        with transaction.atomic():
            print game, count, isize
            count += 1
            gameobject = pbpmodels.Game.objects.get(gamePk=game)
            homeTeam = gameobject.homeTeam.id
            awayTeam = gameobject.awayTeam.id
            pbp = pbpmodels.PlayByPlay.objects.filter(gamePk_id=game).order_by("eventIdx")
            homeScore = 0
            awayScore = 0
            for play in pbp:
                if play.playType == "GOAL":
                    if play.team_id == homeTeam:
                        homeScore += 1
                    else:
                        awayScore += 1
                play.homeScore = homeScore
                play.awayScore = awayScore
                play.save()



if __name__ == "__main__":
    main()
