from django.conf.urls import patterns, url

from stellenplan import views

urlpatterns = patterns('',
    url(r'offeneZusagen', views.offeneZusagen, name='offeneZusagen'),
    url(r'^qStellen$', views.qStellen, name='qStellen'),
)
