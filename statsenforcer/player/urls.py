from django.conf.urls import url
from django.views.decorators.cache import cache_page

from . import views

urlpatterns = [
    url(r'^$', cache_page(86400)(views.players), name='players'),
    url(r'^(?P<player_id>[0-9]+)/$', views.player_page, name='player_page'),
]