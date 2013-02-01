import django_tables2 as tables
from django_tables2.utils import A  # alias for Accessor

import models

class ZusagenTable (tables.Table):
    """Zusagen, nicht aggregiert, mit direktem Durchgriff auf einzelne Zusagenobjekte"""
    
    class Meta:
        model = models.Zusage
        attrs = {'class': 'paleblue'}
    #  some django vodoo
    # compare: https://docs.djangoproject.com/en/dev/ref/contrib/admin/#reversing-admin-urls
    # and: http://django-tables2.readthedocs.org/en/latest/#django_tables2.columns.LinkColumn
    id = tables.LinkColumn ('admin:stellenplan_zusage_change',
                            args=[A('pk')],
                            attrs= {'target': '_blank'})

class StellenTable (tables.Table):
    """Stellen, nicht aggregiert, mit direktem Durchgriff auf einzelne Stellen"""
    class Meta:
        model = models.Stelle
        attrs = {'class': 'paleblue'}
 
    stellennummer = tables.LinkColumn ('admin:stellenplan_stelle_change',
                            args=[A('pk')],
                            attrs= {'target': '_blank'})

class StellenNachWertigkeitTable (tables.Table):
    Wertigkeit = tables.Column()
    Datum = tables.Column()
    Prozent = tables.Column()
    
class StellenNachArtTable (tables.Table):
    Art = tables.Column()
    Datum = tables.Column()
    Prozent = tables.Column()

class StellenNachWertigkeitArtTable (tables.Table):
    Wertigkeit = tables.Column()
    Art = tables.Column()
    Datum = tables.Column()
    Prozent = tables.Column()

class GruppenTable (tables.Table):
    class Meta:
        attrs = {'class': 'paleblue'}
    Gruppe = tables.Column()
    Datum = tables.Column()
    Prozent = tables.Column()
    
