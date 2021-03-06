"""statsenforcer URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.sitemaps import views

from player.sitemap import PlayerSitemap, GoalieSitemap
from playbyplay.sitemap import GameSitemap
from team.sitemap import TeamSitemap
from website.sitemap import StaticSitemap
from django.views.decorators.cache import cache_page

sitemaps = {"skaters": PlayerSitemap, "goalies": GoalieSitemap, "games": GameSitemap, "teams": TeamSitemap, "static" : StaticSitemap}

urlpatterns = [
    url(r'^', include('website.urls')),
    url(r'^players/', include('player.urls')),
    url(r'^teams/', include('team.urls')),
    url(r'^games/', include('playbyplay.urls')),
    url(r'^sitemap\.xml$', cache_page(86400)(views.sitemap), {"sitemaps": sitemaps}),
    url(r'^sitemap-(?P<section>.+)\.xml$', cache_page(86400)(views.sitemap), {'sitemaps': sitemaps},
        name='django.contrib.sitemaps.views.sitemap'),
]

if settings.DEBUG:
    from website.views import custom404, custom500, custom403, custom400
    urlpatterns.extend(
        [url(r'^404/$', custom404),
        url(r'^500/$', custom500),
        url(r'^403/$', custom403),
        url(r'^400/$', custom400)]
    )

handler404 = 'website.views.custom404'
handler500 = 'website.views.custom500'
handler403 = 'website.views.custom403'
handler400 = 'website.views.custom400'
