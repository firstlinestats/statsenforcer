from django.contrib.sitemaps import Sitemap
from django.urls import reverse
import arrow

class StaticSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return ['about', 'glossary']

    def location(self, item):
        return reverse(item)
