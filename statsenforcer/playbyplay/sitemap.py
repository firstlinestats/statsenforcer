from django.contrib.sitemaps import Sitemap
from models import Game
import arrow

class GameSitemap(Sitemap):
    limit = 1000
    changefreq = "daily"
    priority = 0.5

    def items(self):
        return Game.objects.all()

    def lastmod(self, obj):
        if obj.endDateTime:
            return obj.endDateTime
        if obj.gameState in ["1", "2"]:
            return Game.objects.filter(season=obj.season).earliest("dateTime").dateTime
        return arrow.now()

    def location(self, obj):
        return "/games/{}".format(obj.gamePk)
