from django.contrib.sitemaps import Sitemap
from models import Player
import arrow

class PlayerSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return Player.objects.exclude(primaryPositionCode="G")

    def lastmod(self, obj):
        return arrow.now()

    def location(self, obj):
        return "/players/skaters/{}".format(obj.id)


class GoalieSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.5

    def items(self):
        return Player.objects.filter(primaryPositionCode="G")

    def lastmod(self, obj):
        return arrow.now()

    def location(self, obj):
        return "/players/goalies/{}".format(obj.id)
