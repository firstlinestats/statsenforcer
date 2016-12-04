from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^games_header/(?P<gamedate>.*)/', views.games, name='games'),
    url(r'^about/', views.about, name="about"),
    url(r'^glossary/', views.glossary, name="glossary"),
]
