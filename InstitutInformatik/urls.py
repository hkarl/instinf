from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^InstitutInformatik/', include('InstitutInformatik.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^stellenplan/', include('stellenplan.urls')),
    url(r'^$', 'InstitutInformatik.views.home', name='home'),
    # (r'^about/', TemplateView.as_view(template_name="about.html")),
)
