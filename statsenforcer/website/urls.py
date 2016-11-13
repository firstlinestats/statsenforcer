from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^games_header/(?P<gamedate>.*)/', views.games, name='games')
]