from django.conf.urls import url
from django.views.decorators.cache import cache_page

from . import views

urlpatterns = [
    url(r'^skaters/$', views.players, name='skaters'),
    url(r'^skaters/(?P<player_id>[0-9]+)/$', views.player_page, name='player_page'),
    url(r'^goalies/$', views.goalies, name='skaters'),
    url(r'^goalies/(?P<player_id>[0-9]+)/$', views.goalie_page, name='goalie_page'),
]
