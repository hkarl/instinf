from django.db import models 
from django.contrib import admin
from stellenplan.models import Fachgebiet, Stellenart, Stellenwertigkeit, StellenwertigkeitIntervalle, Stelle, Person\
    , Zusage, Zuordnung, Besetzung, PersonZusage
from django_select2 import * 

from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect

import re

###################

# base class that allows to split an entry

class SplitOnDateAdmin (admin.ModelAdmin):
    actions= ['EintragTeilen']
    
    def EintragTeilen (self, request, queryset):
        selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
        ## print "---- cr ----"
        ## ct = ContentType.objects.get_for_model(queryset.model)
        ## print ct
        ## print type(ct)
        target= re.sub('Admin', '', self.__class__.__name__).lower()
        return HttpResponseRedirect("/stellenplan/split/{0:s}/?ids={1:s}".format(target, ",".join(selected)))

    # splitPerson.short_description ("Teile den Datensatz einer Person an einem anzugebenden Datum")


###################


class FachgebietAdmin (SplitOnDateAdmin):
    list_display = ['kuerzel', 'fgname', 'von', 'bis', 'kostenstelle',]
    
class StellenartAdmin (admin.ModelAdmin):
    list_display = ['stellenart']
    
class StellenwertigkeitAdmin (admin.ModelAdmin):
    list_display = ['wertigkeit']

class StellenwertigkeitIntervalleAdmin (SplitOnDateAdmin):
    list_display = ['wertigkeit', 'von', 'bis', 'personalpunkte']


class StelleAdmin (SplitOnDateAdmin):
    list_display = ['stellennummer', 'wertigkeit', 'art', 'lehrkapazitaet', 'von', 'bis', 'prozent']
    
class PersonAdmin (SplitOnDateAdmin):
    list_display = ['personalnummer', 'name', 'vorname']
    search_fields = ['personalnummer', 'name']
    ordering = ['personalnummer', 'name']

class PersonZusageAdmin (SplitOnDateAdmin):
    list_display = ['person', 'wertigkeit', 'lehrverpflichtung', 'von', 'bis', 'prozent']
    search_fields = ['person']
    ordering = ['person', 'von']


class ZusageAdmin (SplitOnDateAdmin):
    list_display = ['fachgebiet', 'wertigkeit', 'prozent', 'von', 'bis',]
    # search_fields = ['fachgebiet'] - ForeignKeys kann man wohl nicht als search_fields nehmen? 
    
class ZuordnungAdmin (SplitOnDateAdmin):
    list_display = ['fachgebiet', 'stelle', 'prozent', 'von', 'bis',]

    # This is an attempt to put Select2ChoiceField into the admin interface for foreignkeys,
    # but that does not work as suspected
    # check: https://docs.djangoproject.com/en/dev/ref/contrib/admin/#django.contrib.admin.ModelAdmin.formfield_overrides 
    ## formfield_overrides = {
    ##     models.ForeignKey: {'widget': Select2ChoiceField },
    ## }
    
class BesetzungAdmin (SplitOnDateAdmin):
    list_display = ['person', 'stelle', 'prozent', 'von', 'bis', 'pseudo']
    # search_fields = ['person', 'stelle']


admin.site.register (Fachgebiet, FachgebietAdmin)
admin.site.register (Stellenart, StellenartAdmin)
admin.site.register (Stellenwertigkeit, StellenwertigkeitAdmin)
admin.site.register (StellenwertigkeitIntervalle, StellenwertigkeitIntervalleAdmin)
admin.site.register (Stelle, StelleAdmin)
admin.site.register (Person, PersonAdmin)
admin.site.register (PersonZusage, PersonZusageAdmin)
admin.site.register (Zusage, ZusageAdmin)
admin.site.register (Zuordnung, ZuordnungAdmin)
admin.site.register (Besetzung, BesetzungAdmin)
