from django.conf.urls import url
from django.views.decorators.cache import cache_page

from . import views

urlpatterns = [
    url(r'^$', views.players, name='players'),
    url(r'^(?P<player_id>[0-9]+)/$', views.player_page, name='player_page'),
]