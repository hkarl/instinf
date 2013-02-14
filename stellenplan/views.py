# -*- coding: utf-8 -*-

# from django.http import HttpResponse
from django.views.generic import ListView, View
from django.shortcuts import render
from stellenplan.models import * 
from stellenplan.timeline import Timeline, TimelineGroups
from django.forms.widgets import CheckboxSelectMultiple
import tables
from django_tables2   import RequestConfig
import django_tables2 
from pprint import pprint as pp 
import accordion 
from django.views.decorators.http import require_http_methods
from stellenplanForms import * 


def standardfilters (qs, keywords, cleaned_data):
    """Apply all the filter keywords to the queryset, take values from cleaned_data.
    Von and Bis are always applied, nbo need to specify them in the keywords """

    ## print "standardfilters: ", keywords
    ## print pp(cleaned_data)

    if cleaned_data['Von']:
        qs = qs.exclude (bis__lt = cleaned_data['Von'])
    if cleaned_data['Bis']:
        qs = qs.exclude (von__gt = cleaned_data['Bis'])

    for k in keywords:
        if not (cleaned_data[k] == '-----'):
            filterstring = k.lower() + '__exact'
            print filterstring 
            qs = qs.filter (**{filterstring: cleaned_data[k]})

    return qs 



#########################################################

class stellenplanQuery (View):

    additionalFields = {}
    """
    additional fields is a dictionary, mapping field names to defaults. 
    """

    urlTarget = ''
    queryFormClass = qForm 
        
    def constructAccordion (self, request):
        """
        construct the renderDir dictionary, containting the filter results in
        accprdions.
        """
        return [] 
    
    def get(self, request):
        # print request 
        if not request.method == 'GET':
            return  HttpResponseNotFound('<h1>Request type not supported!</h1>')

        if request.GET:
            # es gibt schon eine Anfrage
            self.ff = self.__class__.queryFormClass (request.GET)
            if not self.ff.is_valid():
                print "error"
                return render (request,
                               url,
                               {'error_message': 'Bitte berichtigen Sie folgenden Fehler: ',
                               'form': self.ff,
                               'urlTarget': self.__class__.urlTarget,                           
                                   })
            
        else:
            # empty request, neu aufbauen
            print "empty request!" 
            self.ff = self.__class__.queryFormClass (request.GET)
            self.ff.cleaned_data = {'Von': None,
                                    'Bis': None}
            self.ff.cleaned_data.update(self.__class__.additionalFields)


        self.renderDir = {
            'form': self.ff,
            'urlTarget': self.__class__.urlTarget,
            }

        ## pp(self.renderDir) 
        ## print self.renderDir['form']
        self.renderDir['Accordion'] = []
        self.constructAccordion (request)

        return render (request,
                       "stellenplan/" + self.__class__.urlTarget + ".html",
                       self.renderDir)

        


#################################

    
class qBesetzung (stellenplanQuery):
    """This is just an empty class"""
    urlTarget = 'qBesetzung'
    queryFormClass = BesetzungFilterForm 


    def constructAccordion (self, request):
        # print "filtering according to Besetzung" 

        ########################################
        #  die Besetzungen wie üblich filtern: 
        allBesetzung = Besetzung.objects.all()

        # alle Besetzungen nach Standardfilter 
        qs = standardfilters (allBesetzung, [], self.ff.cleaned_data)
        besetzungstab = tables.BesetzungTable (qs)
        RequestConfig (request).configure(besetzungstab)

        a = accordion.Accordion ("Besetzungen")
        a.addContent (besetzungstab)

        self.renderDir['Accordion'].append(a)
        ########################################



#########################################################


class qStellen (stellenplanQuery):
    urlTarget = "qStellen"
    queryFormClass = StellenFilterForm
    additionalFields = {'Wertigkeit': '-----',
                        'Art': '-----'}
    

    def constructAccordion (self, request):
        # print "filtering according to Besetzung" 

        ac = []

        ########################################
        #  die Stellen wie üblich filtern: 
        allStellen = Stelle.objects.all()

        # alle Besetzungen nach Standardfilter 
        qs = standardfilters (allStellen,
                              ['Wertigkeit', 'Art'],
                              self.ff.cleaned_data)
        stellentab = tables.StellenTable (qs) 
        RequestConfig (request).configure(stellentab)

        a = accordion.Accordion ("Stellen insgesamt")
        a.addContent (stellentab)

        self.renderDir['Accordion'].append(a)

        ########################################

        # gefilterte Stellen nach Wertigkeit zusammenfassen
        tgWertigkeit = TimelineGroups (qs,'wertigkeit')
        tgWertigkeit.asAccordion ("Stellen nach Wertigkeit gruppiert",
                                  self.renderDir, request)

        #########

        # gefilterte Stellen nach Finanzierung zusammenfassen
        TimelineGroups (qs,
                        'art').asAccordion ("Stellen nach Finanzierung gruppiert",
                                            self.renderDir, request)



        ########################################

        # von den Stellen die Zusagen abziehen
        # ziehe von den Stellen die Zusagen ab.
        # Dazu erstmal die Zusagen entsprechend filtern,
        # dann ueber timelinegroups verarbeiten.
        # Da nur StellenTYPEN, aber nicht spezifischer STellen
        # zugesagt werdne, macht es keinen Sinn,
        # das individuell pro Stellen zu machen, sondern nur für
        # entsprechende Aggregierungen


        zusageQs = standardfilters (Zusage.objects.all(),
                                    ['Wertigkeit'], self.ff.cleaned_data)
        tgZusageWertigkeit = TimelineGroups (zusageQs, 'wertigkeit')
        tgWertigkeitOhneZusagen = tgWertigkeit.subtract(tgZusageWertigkeit)

        tgWertigkeitOhneZusagen.asAccordion ("Stellen nach Wertigkeit gruppiert, Zusagen abgezogen",
                                             self.renderDir, request)
        
        
        ########################################

    
    
#########################################################
#########################################################
#########################################################

@require_http_methods(["GET"])
def qStellen_func (request):
    # decorator guarantess only GET makes it here
    

    if request.GET:
        # es gibt schon eine Anfrage
        ff = StellenFilterForm (request.GET)
        if not ff.is_valid():
            print "error"
            return render (request,
                           url,
                           {'error_message': 'Bitte berichtigen Sie folgenden Fehler: ',
                           'form': ff,
                           'urlTarget': 'qStellen',                           
                               })
        
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

    
    # die Tabellen für die Ausgabe via django_tables2 zusammenbauen 
    stellentab = tables.StellenTable (qs2) 
    RequestConfig (request).configure(stellentab)

    # fasse die gefilterten DAten zu Gruppen zusammen
    tgArt = TimelineGroups (qs2, 'art')
    tgWertigkeit = TimelineGroups (qs2, 'wertigkeit')
    
    # ziehe von den Stellen die Zusagen ab. Dazu erstmal die Zusagen entsprechend filtern,
    # dann ueber timelinegroups verarbeiten. Da nur StellenTYPEN, aber nicht spezifischer STellen
    # zugesagt werdne, macht es keinen Sinn, das individuell pro Stellen zu machen, sondern nur für
    # entsprechende Aggregierungen

    zusageQs = standardfilters (Zusage.objects.all(),  ['Wertigkeit'], ff.cleaned_data)
    tgZusageWertigkeit = TimelineGroups (zusageQs, 'wertigkeit')
    
    tgWertigkeitOhneZusagen = tgWertigkeit.subtract(tgZusageWertigkeit)

    # und noch die render-Ifnormation zusammensetzen, insbes. um die Accordions und tabs automatisch aufbauen zu können 
    
    renderDir =  {'form': ff,
                  'urlTarget': 'qStellen',
                  }


    ac = accordion.Accordion ("Stellen insgesamt")
    ac.addContent (stellentab)
    renderDir['Accordion'] = [ac] 
    
    tgArt.asAccordion ("Stellen nach Finanzierung gruppiert", renderDir, request)
    tgWertigkeit.asAccordion ("Stellen nach Wertigkeit gruppiert", renderDir, request)
    tgWertigkeitOhneZusagen.asAccordion ("Stellen nach Wertigkeit gruppiert, Zusagen abgezogen",
                                         renderDir, request)

    # pp(renderDir)
    # print renderDir['form']
    return render (request,
                   "stellenplan/qStellen.html",
                   renderDir)

##############################################################


def qZusagen(request):
    """
    Abfragen für Zusagen.
    Filter nach Datum, Fachgebiet, Wertigkeit.
    Zusagen sind durch Zuordnungen unterlegt; interessant sind also Zusagen, für die
    es keine Zuordnungen gibt. 
    """

    # Version mit forms Library:



    ################
    if not request.method == 'GET':
        return HttpResponseNotFound('<h1>Request type not supported!</h1>')


    if request.GET:
        # es gibt schon eine Anfrage
        # pp (request.GET)
        ff = zusagenFilterForm (request.GET)
        if not ff.is_valid():
            print "error"
            return render (request,
                           url,
                           {'error_message': 'Bitte berichtigen Sie folgenden Fehler: ',
                           'form': ff,
                           'urlTarget': 'qStellen',                           
                               })
        
    else:
        # empty request, neu aufbauen 
        ff = zusagenFilterForm ()
        ff.cleaned_data = {'Fachgebiet': '-----',
                           'Wertigkeit': '-----',
                           'Von': None,
                           'Bis': None}

    renderDir =  {'form': ff,
                  'urlTarget': 'qZusagen',
                  }


    qs = standardfilters (Zusage.objects.all(), ['Fachgebiet', 'Wertigkeit'], ff.cleaned_data)

    overviewtab = tables.ZusagenTable (qs)
    RequestConfig (request).configure(overviewtab)

    ac = accordion.Accordion("Zusagen insgesamt")
    ac.addContent (overviewtab)
    renderDir['Accordion'] = [ac]

    tgWertigkeit = TimelineGroups(qs, 'wertigkeit')
    tgWertigkeit.asAccordion ("Zusagen, nach Wertigkeit gruppiert",
                             renderDir, request)

        # Zuordnungen abziehen:
        # hier muss man noch einen join mit Stellen machen, ob die tatsächliche Stellenwertigkeit zu bekommen? 
    qsZuordnung = standardfilters (Zuordnung.objects.all(),
                                   ['Fachgebiet'],
                                   ff.cleaned_data)
    pp ([z for z in  qsZuordnung])
    if not ff.cleaned_data['Wertigkeit'] == '-----':
        qsZuordnung = qsZuordnung.filter (stelle__wertigkeit__exact = ff.cleaned_data['Wertigkeit'])

    pp ([z for z in  qsZuordnung])
    
    tgZuordnungWertigkeit = TimelineGroups(qsZuordnung, 'stelle__wertigkeit')
    tgZusagenOhneZuordnung = tgWertigkeit.subtract(tgZuordnungWertigkeit)
    tgZusagenOhneZuordnung.asAccordion ("Offene Zusagen (Zuordnungen sind abgezogen), nach Wertigkeit gruppiert",
                                        renderDir, request)
    
    return render (request,
                   "stellenplan/qZusagen.html",
                   renderDir)



        #################################################################
                               ########  OLD CODE 
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

