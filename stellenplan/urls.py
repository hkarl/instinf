from django.conf.urls import patterns, url
from django.conf import settings

from stellenplan import views

urlpatterns = patterns('',
    url(r'qZusagen', views.qZusagen, name='qZusagen'),
    url(r'^qStellen$', views.qStellen, name='qStellen'),
)
