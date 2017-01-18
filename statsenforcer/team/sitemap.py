from django.contrib.sitemaps import Sitemap
from models import Team
import arrow

class TeamSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return Team.objects.all()

    def lastmod(self, obj):
        return arrow.now()

    def location(self, obj):
        return u"/teams/{}".format(obj.shortName)
