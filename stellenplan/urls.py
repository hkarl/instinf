from django.conf.urls import patterns, url
from django.conf import settings

from stellenplan import views, consistency 


urlpatterns = patterns('',
    #url(r'qZusagen', views.qZusagen, name='qZusagen'),
    url(r'qZusagen', views.qZusagen.as_view(), name='qZusagen'),
    # url(r'^qStellen$', views.qStellen, name='qStellen'),
    url(r'^qStellen$', views.qStellen.as_view(), name='qStellen'),
    url(r'^qBesetzung$', views.qBesetzung.as_view(), name='qBesetzung'),
    url(r'qZuordnungen', views.qZuordnungen.as_view(), name='qZuordnungen'),
    url(r'konsistenz', consistency.konsistenz.as_view(), name='konsistenz'),
)
