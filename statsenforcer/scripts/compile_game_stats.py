import os
import sys
import django

import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), "statsenforcer"))
sys.path.append("../")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "statsenforcer.settings")
from django.conf import settings

django.setup()

from playbyplay.models import Game, PlayByPlay
from team.models import TeamGameStats

import queries


def compile_info(gameId):
	pass


def main():
	games = TeamGameStats.objects.values_list("game_id", flat=True).all()
	mgames = Game.objects.values_list("gamePk", flat=True).exclude(gamePk__in=games)\
		.filter(gameState__in=["5", "6", "7"], season=20162017)
	for game in mgames:
		pbp = list(PlayByPlay.objects.raw(queries.playbyplayquery, [game, ]))
		print len(pbp)
		break


if __name__ == "__main__":
	main()
