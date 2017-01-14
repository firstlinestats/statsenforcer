from django.contrib.sitemaps import Sitemap
from models import Player
import arrow

class PlayerSitemap(Sitemap):
    limit = 1000
    changefreq = "daily"
    priority = 0.5

    def items(self):
        return Player.objects.all()

    def lastmod(self, obj):
        return arrow.now()

    def location(self, obj):
        return "/players/{}".format(obj.id)
