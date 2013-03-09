from django.conf.urls import patterns, url
from django.conf import settings
from django.views.generic import TemplateView

from stellenplan import views

urlpatterns = patterns('',
    #url(r'qZusagen', views.qZusagen, name='qZusagen'),
    url(r'qZusagen', views.qZusagen.as_view(), name='qZusagen'),
    # url(r'^qStellen$', views.qStellen, name='qStellen'),
    url(r'^qStellen$', views.qStellen.as_view(), name='qStellen'),
    url(r'^qBesetzung$', views.qBesetzung.as_view(), name='qBesetzung'),
    url(r'qZuordnungen', views.qZuordnungen.as_view(), name='qZuordnungen'),
    # url(r'split', views.split.as_view(), name='split'),
    # url(r'split', "stellenplan/split.html", name='split'),
    url(r'split/(?P<what>[a-zA-Z]+)/', TemplateView.as_view(template_name="stellenplan/split.html")),
    url(r'splitAction/(?P<what>[a-zA-Z]+)/', views.split.as_view(), name="splitAction"),
    # url(r'splitAction', views.split.as_view(), name="splitAction"),
)
