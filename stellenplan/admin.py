from django.db import models 
from django.contrib import admin
from stellenplan.models import Fachgebiet, Stellenart, Stellenwertigkeit, Stelle, Person, Zusage, Zuordnung, Besetzung
from django_select2 import * 


class FachgebietAdmin (admin.ModelAdmin):
    list_display = ['kuerzel', 'fgname', 'von', 'bis', 'kostenstelle',]
    
class StellenartAdmin (admin.ModelAdmin):
    list_display = ['stellenart']
    
class StellenwertigkeitAdmin (admin.ModelAdmin):
    list_display = ['wertigkeit', 'personalpunkte']
    
class StelleAdmin (admin.ModelAdmin):
    list_display = ['stellennummer', 'wertigkeit', 'art', 'von', 'bis', 'prozent']
    
class PersonAdmin (admin.ModelAdmin):
    list_display = ['personalnummer', 'name', 'vorname', 'wertigkeit', 'von', 'bis', 'prozent']
    search_fields = ['name']
    
class ZusageAdmin (admin.ModelAdmin):
    list_display = ['fachgebiet', 'wertigkeit', 'prozent', 'von', 'bis',]
    # search_fields = ['fachgebiet'] - ForeignKeys kann man wohl nicht als search_fields nehmen? 
    
class ZuordnungAdmin (admin.ModelAdmin):
    list_display = ['fachgebiet', 'stelle', 'prozent', 'von', 'bis',]

    # This is an attempt to put Select2ChoiceField into the admin interface for foreignkeys,
    # but that does not work as suspected
    # check: https://docs.djangoproject.com/en/dev/ref/contrib/admin/#django.contrib.admin.ModelAdmin.formfield_overrides 
    ## formfield_overrides = {
    ##     models.ForeignKey: {'widget': Select2ChoiceField },
    ## }
    
class BesetzungAdmin (admin.ModelAdmin):
    list_display = ['person', 'stelle', 'prozent', 'von', 'bis', 'pseudo']
    # search_fields = ['person', 'stelle']


admin.site.register (Fachgebiet, FachgebietAdmin)
admin.site.register (Stellenart, StellenartAdmin)
admin.site.register (Stellenwertigkeit, StellenwertigkeitAdmin)
admin.site.register (Stelle, StelleAdmin)
admin.site.register (Person, PersonAdmin)
admin.site.register (Zusage, ZusageAdmin)
admin.site.register (Zuordnung, ZuordnungAdmin)
admin.site.register (Besetzung, BesetzungAdmin)
