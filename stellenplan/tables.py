import django_tables2 as tables
from django_tables2.utils import A  # alias for Accessor

import models
import django.db
import re

# from django.db import models


class latexableTable (tables.Table):

    """  
    Intermediate class to teach django tables to output themselves as LaTeX code.
    Class-based attributes control behvaior:  
    - fieldsForLaTeX is a list with the column names that should be output; if empty, all columsn. column names correspond to the field names in the model 
    - columnwidthForLatex is a list with STRINGS that have p{} parameters for column width (not yet implemented) 
    """
    fieldsForLatex = None
    columnwidthForLatex = None
    
    def aslatex(self):

        r = ""
        # generate prefix
        r += '\\begin{tabular}'

        # write header row
        ## example code: 
        ## for c in self.columns:
        ##     print c.name, c.header
        ## print self.columns['von'].header

        if self.__class__.fieldsForLatex:
            if self.__class__.columnwidthForLatex: 
                r += '{' +   self.__class__.columnwidthForLatex +'}\n'
            else: 
                r += '{' +  'c' * len(self.__class__.fieldsForLatex)  +'}\n'
            r += '\\toprule\n'
            r += ' & '.join([self.columns[c].header
                             for c in self.__class__.fieldsForLatex])
            outputcolumns = self.__class__.fieldsForLatex
        else:
            r += '{' +  'c' * len(self.columns)  +'}\n'
            r += '\\toprule\n'
            r += ' & '.join([c.header for c in self.columns])
            outputcolumns = [c.name for c in self.columns]
            
        r += '\\\\  \n \\midrule \n'

        # write rows 
        for row in self.rows:
            ca = []
            
            for col in outputcolumns:
                cell = row[col]
                # print cell 
                # print type(cell)
                if isinstance(cell, unicode):
                    s = cell
                else: 
                    try:
                        s = cell.__unicode__()
                    except:
                        s = cell.__str__()


                ca.append(re.sub ('<.*?>', '', s))

            r += ' & '.join(ca) + '\\\\ \n'


                ## print cell
                ## print cell.__repr__()
                ## print cell.__unicode__()
                ## print type(cell)
                # r += cell 
                # r += re.sub (cell, '<[^>]*>', '')

        # wrtie suffix 
        r += '\\bottomrule\n'
        r += '\\end{tabular}\n'

        # print r 
        return r 


class ZusagenTable (latexableTable):
    """Zusagen, nicht aggregiert, mit direktem Durchgriff auf einzelne Zusagenobjekte"""
    
    fieldsForLatex = ['fachgebiet', 'wertigkeit', 'prozent', 'von', 'bis']

    class Meta:
        model = models.Zusage
        attrs = {'class': 'paleblue'}
    #  some django vodoo
    # compare: https://docs.djangoproject.com/en/dev/ref/contrib/admin/#reversing-admin-urls
    # and: http://django-tables2.readthedocs.org/en/latest/#django_tables2.columns.LinkColumn
    id = tables.LinkColumn ('admin:stellenplan_zusage_change',
                            args=[A('pk')],
                            attrs= {'target': '_blank'})



# #################################

class BesetzungTable (latexableTable):

    fieldsForLatex = ['person', 'stelle', 'prozent', 'von', 'bis']
    columnwidthForLatex = r'p{0.2\textwidth}p{0.4\textwidth}ccc'

    class Meta:
        model = models.Besetzung
        attrs = {'class': 'paleblue'}

    id = tables.LinkColumn ('admin:stellenplan_besetzung_change',
                            args=[A('pk')],
                            attrs= {'target': '_blank'})
    
                      

# #################################
 
class StellenTable (latexableTable):
    """Stellen, nicht aggregiert, mit direktem Durchgriff auf einzelne Stellen"""

    fieldsForLatex = ['stellennummer', 'wertigkeit', 'art', 'prozent', 'von', 'bis']
    class Meta:
        model = models.Stelle
        attrs = {'class': 'paleblue'}
 
    stellennummer = tables.LinkColumn ('admin:stellenplan_stelle_change',
                            args=[A('pk')],
                            attrs= {'target': '_blank'})

# #################################


class StellenNachWertigkeitTable (latexableTable):
    Wertigkeit = tables.Column()
    Datum = tables.Column()
    Prozent = tables.Column()

# #################################

    
class StellenNachArtTable (latexableTable):
    Art = tables.Column()
    Datum = tables.Column()
    Prozent = tables.Column()

# #################################


class StellenNachWertigkeitArtTable (latexableTable):
    Wertigkeit = tables.Column()
    Art = tables.Column()
    Datum = tables.Column()
    Prozent = tables.Column()

# #################################


class GruppenTable (latexableTable):
    class Meta:
        attrs = {'class': 'paleblue'}
    Gruppe = tables.Column()
    Datum = tables.Column()
    Prozent = tables.Column()
    
