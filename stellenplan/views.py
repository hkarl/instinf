# -*- coding: utf-8 -*-

# from django.http import HttpResponse
from django.views.generic import ListView
from django.shortcuts import render
from stellenplan.models import * 
from stellenplan.timeline import Timeline, TimelineGroups
from django import forms
from django.forms.widgets import CheckboxSelectMultiple
import tables
from django_tables2   import RequestConfig
import django_tables2 


def standardfilters (qs, keywords, cleaned_data):
    """Apply all the filter keywords to the queryset, take values from cleaned_data.
    Von and Bis are always applied, nbo need to specify them in the keywords """

    if cleaned_data['Von']:
        qs = qs.exclude (bis__lt = cleaned_data['Von'])
    if cleaned_data['Bis']:
        qs = qs.exclude (von__gt = cleaned_data['Bis'])

    for k in keywords:
        if not (cleaned_data[k] == '-----'):
            filterstring = k.lower() + '__exact'
            qs = qs.filter (**{filterstring: cleaned_data[k]})

    return qs 

def qStellen (request):

    class StellenFilterForm (forms.Form):
        Wertigkeit = forms.fields.ChoiceField (choices=[('-----', '----')]
                                               + sorted([(x.wertigkeit,x.wertigkeit)
                                                  for x in Stellenwertigkeit.objects.all() ]),
                                                required=False)
        Art =  forms.fields.ChoiceField (choices=[('-----', '----')]
                                               + sorted([(x.stellenart,x.stellenart)
                                                  for x in Stellenart.objects.all() ]),
                                                required=False)
        Von = forms.fields.DateField(required=False)
        Bis = forms.fields.DateField(required=False)


    ################
    if not request.method == 'GET':
        return HttpResponseNotFound('<h1>Request type not supported!</h1>')


    if request.GET:
        # es gibt schon eine Anfrage
        ff = StellenFilterForm (request.GET)
        ff.is_valid()
    else:
        # empty request, neu aufbauen 
        ff = StellenFilterForm ()
        ff.cleaned_data = {'Wertigkeit': '-----',
                           'Art': '-----',
                           'Von': None,
                           'Bis': None}

    # apply any filters:
    qs = Stelle.objects.all()
    
    qs2 = standardfilters (qs, ['Wertigkeit', 'Art'], ff.cleaned_data)
    # aggregiere die so gefilterten Daten nach Wertigkeit und nach Stelle,
    # baue daraus eine Timeline auf

    # die Tabellen für die Ausgabe via django_tables2 zusammenbauen 
    stellentab = tables.StellenTable (qs2) 
    RequestConfig (request).configure(stellentab)


    return render (request,
                   "stellenplan/qStellen.html",
                   {'form': ff,
                    'stellen': stellentab,
                    'gruppe': TimelineGroups (qs2, 'art').asTable(request),
                    'wertigkeit': TimelineGroups (qs2, 'wertigkeit').asTable(request),
                       })


def offeneZusagen(request):


    # Version mit forms Library:

    class offeneZusagenFilter (forms.Form):
        Fachgebiet = forms.fields.ChoiceField (choices=[('-----', '----')]
                                               + [(x,x) for x in Fachgebiet.objects.all() ],
            required=False)
        Wertigkeit = forms.fields.ChoiceField (choices=[('-----', '----')]
                                               + [(x.wertigkeit,x.wertigkeit) for x in Stellenwertigkeit.objects.all() ],
            required=False)
        Von = forms.fields.DateField(required=False)
        Bis = forms.fields.DateField(required=False)
        Auswahl = forms.fields.MultipleChoiceField (widget=CheckboxSelectMultiple,
                                                    required=False, 
                                                    choices = [('komplettoffen', 'Komplette offene Zusagen'),
                                                               ('teilweise', 'Teilweise offene Zusagen'),
                                                               ('erfuellt','Erfüllte Zusagen')],
                                                    initial= ['komplettoffen', 'teilweise','erfuellt',],
            )

    class wertig_table (django_tables2.Table):
        Fachgebiet = django_tables2.Column()
        Wertigkeit = django_tables2.Column()
        Datum = django_tables2.Column()
        Prozent = django_tables2.Column()

    print ">>>> request: "
    print request
    print 
    
    if request.method=='POST':
        results = Zusage.objects.all()
        ff = offeneZusagenFilter (request.POST)
        if ff.is_valid():
            print ff.cleaned_data
        else:
            print "form is not valid!" 

        if not (ff.cleaned_data['Fachgebiet'] == '-----'):
            results = results.filter (fachgebiet__exact=ff.cleaned_data['Fachgebiet'])

        if not (ff.cleaned_data['Wertigkeit'] == '-----'):
            results = results.filter (wertigkeit__exact=ff.cleaned_data['Wertigkeit'])        

        if ff.cleaned_data['Von']:
            results = results.exclude (bis__lt = ff.cleaned_data['Von'])

        if ff.cleaned_data['Bis']:
            results = results.exclude (von__gt = ff.cleaned_data['Bis'])



        # Zusammenfassung nach Wertigkeiten, und dann auf Timeline verteilen:
        wertig_tab = []
        for wertig in Stellenwertigkeit.objects.all():
            res_wertig = results.filter(wertigkeit__exact=wertig.wertigkeit)
            if res_wertig:
                print "Wertigkeit " + wertig.wertigkeit + " kommt vor"

                # collect  all the dates into timeline
                tl = Timeline()

                for x in res_wertig:
                    tl.add(x.von, x.bis, x.prozent)

                    
                wertig_tab.extend(tl.aslist({'Fachgebiet': ff.cleaned_data['Fachgebiet'],
                                             'Wertigkeit': wertig.wertigkeit}))

            # nothing needs to be done if this wertigkeit does not appear

    else:
        print 'without post'
        ff = offeneZusagenFilter ()
        results = []
        wertig_tab = []
        # print ff.fields['Auswahl']

    ###################################################
    # und noch die Tabelle zusammen bauen
    table = tables.ZusagenTable (results)
    RequestConfig (request).configure(table)
    
    wt = wertig_table(wertig_tab)
    RequestConfig (request).configure(wt)
    
    return render (request,
                   'stellenplan/offeneZusagen-Lib.html',
                   {'form': ff,
                    # 'zusagen': results},
                    'zusagen': table,
                    'wertigzusammenfassung': wt},
        )
        


class offeneStellenList (ListView):
    model = Stelle
    template_name = "stellenplan/offeneStellen.html"
    context_object_name = "stellen"

