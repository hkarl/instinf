from django.conf.urls import patterns, url
from django.conf import settings

from stellenplan import views

urlpatterns = patterns('',
    url(r'qZusagen', views.qZusagen, name='qZusagen'),
    # url(r'qZuordnungen', views.qZuordnungen, name='qZuordnungen'),
    url(r'^qStellen$', views.qStellen, name='qStellen'),
    url(r'^qBesetzung$', views.qBesetzung.as_view(), name='qBesetzung'),
)
