from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^games_header/(?P<gamedate>.*)/', views.games, name='games'),
    url(r'^about/', views.about, name="about"),
    url(r'^glossary/', views.glossary, name="glossary"),
    url(r'^standings/', views.standings, name="standings"),
    url(r'^rink/', views.rink, name="rink"),
    url(r'^team/(?P<team_abbreviation>[a-zA-Z]+)', views.team_logo, name='teamlogo'),
    url(r'^search/', views.search, name='search'),
]
