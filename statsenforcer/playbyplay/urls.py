from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^(?P<game_pk>[0-9]+)/$', views.game, name='game'),
]