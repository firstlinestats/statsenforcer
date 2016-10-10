from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^(?P<team_name>[\w\-]+)/$', views.team_page, name='team_page'),
]