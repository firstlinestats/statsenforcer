from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.teams, name='teams'),
    url(r'^(?P<team_name>[\w\-]+)/$', views.team_page, name='team_page'),
]