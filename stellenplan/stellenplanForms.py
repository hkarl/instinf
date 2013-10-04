# -*- coding: utf-8 -*-
from django import forms
from stellenplan.models import * 
from django_select2 import * 

class qForm (forms.Form):
    """
    Base class for all the forms used in the Stellenplan application.
    It provides two date fileds and checks they are in the right order. 
    """
    Von = forms.fields.DateField(required=False)
    Bis = forms.fields.DateField(required=False)
    PDF = forms.fields.BooleanField (required=False,
                                     label="PDF erzeugen?",
                                     initial=False,
        )
    
    def clean(self):
        cleaned_data = super(qForm, self).clean()
        
        if (cleaned_data['Von'] and
            cleaned_data['Bis'] and
            cleaned_data['Von'] > cleaned_data['Bis']):
            # print "raising error"
            raise forms.ValidationError ("Das Von Datum muss vor dem Bis Datum liegen.")
        return cleaned_data 


#################################

class BesetzungFilterForm (qForm):
    # find out how Besetzungen should be filtered

    # Idea 1: Filter according to a particular person

    Person = Select2ChoiceField (choices=[('-----', '----')]
                                           + sorted([(x.personalnummer,x.__unicode__())
                                              for x in Person.objects.all() ]),
                                            required=False,
                widget = Select2Widget(select2_options={'minimumResultsForSearch': 2,
                                                        'placeholder': u'----',
                                                        'width': u'resolve', 
                                                        'allowClear': 'false', 
                                                }))

    # IDeas 2: filter according to Stellennummer 

    Stellennummer = Select2ChoiceField (choices=[('-----', '----')]
                                           + sorted([(s.stellennummer, s.__unicode__())
                                              for s in Stelle.objects.all() ]),
                                            required=False,
                widget = Select2Widget(select2_options={'minimumResultsForSearch': 2,
                                                        'placeholder': u'----',
                                                        'width': u'resolve', 
                                                        'allowClear': 'false', 
                                                }))


    # IDea 2: Filter all those persons who hold a Stelle in a given Fachgebiet
    # That needs further thought 
    ## Fachgebiet = forms.fields.ChoiceField (choices=[('-----', '----')]
    ##                                        + [(x,x) for x in Fachgebiet.objects.all() ],
    ##     required=False)
    
#################################

class StellenFilterForm (qForm):
    Wertigkeit = Select2ChoiceField (choices=[('-----', '----')]
                                           + sorted([(x.wertigkeit,x.wertigkeit)
                                              for x in Stellenwertigkeit.objects.all() ]),
                                            required=False)
    Art =  Select2ChoiceField (choices=[('-----', '----')]
                                           + sorted([(x.stellenart,x.stellenart)
                                              for x in Stellenart.objects.all() ]),
                                            required=False)

#################################
class zuordnungenFilterForm (qForm):
    Fachgebiet = Select2ChoiceField (choices=[('-----', '----')]
                                           + [(x,x) for x in Fachgebiet.objects.all() ],
        required=False)

#################################

    
class zusagenFilterForm (qForm):
    Fachgebiet = Select2ChoiceField (choices=[('-----', '----')]
                                           + [(x,x) for x in Fachgebiet.objects.all() ],
        required=False)
    Wertigkeit = Select2ChoiceField (choices=[('-----', '----')]
                                               + [(x.wertigkeit,x.wertigkeit)
                                               for x in Stellenwertigkeit.objects.all() ],
        required=False)
        ## Auswahl = forms.fields.MultipleChoiceField (widget=CheckboxSelectMultiple,
        ##                                             required=False, 
        ##                                             choices = [('komplettoffen', 'Komplette offene Zusagen'),
        ##                                                        ('teilweise', 'Teilweise offene Zusagen'),
        ##                                                        ('erfuellt','Erfüllte Zusagen')],
        ##                                             initial= ['komplettoffen', 'teilweise','erfuellt',],
        ## )

    def clean(self):
        cleaned_data = super(zusagenFilterForm, self).clean()
        
        # print Fachgebiet, cleaned_data['Fachgebiet']
        if ((cleaned_data['Fachgebiet'] != '-----') and
            (cleaned_data['Wertigkeit'] == '-----')):
            # get alle Wertigkeiten, die dieses Fachgebiet betreffen und
            # bauen den WErtigkeitsbutton neu zusammen
            
            wertig = Zusage.objects.all().filter (fachgebiet__kuerzel__exact=
                                                  cleaned_data['Fachgebiet']).values('wertigkeit').distinct()
            # print wertig 
            self.fields['Wertigkeit'].choices  =  ([('-----', '----')]
                                                   + [(x['wertigkeit'],
            x['wertigkeit'])
                                                       for x in wertig ])
            
        return cleaned_data 
        
        
