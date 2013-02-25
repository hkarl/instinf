# -*- coding: utf-8 -*-

# from django.http import HttpResponse
from django.conf import settings
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
import os, codecs
import subprocess 


from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

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
        if not ((cleaned_data[k] == '-----') or
                (cleaned_data[k] == '')):
            filterstring = k.lower() + '__exact'
            # print filterstring 
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
    emptyFieldIndicator = '-----'
        
    def constructAccordion (self, request):
        """
        construct the renderDir dictionary, containting the filter results in
        accprdions.
        """
        return [] 


    def producePDF (self):
        # print 'Media:', settings.STATICFILES_DIRS[0]

        workdir = settings.STATICFILES_DIRS[0]
        fp = os.path.join(settings.STATICFILES_DIRS[0], 'report.tex')
        
        preface = r"""
        \documentclass{article}
        \usepackage{booktabs}
        \usepackage{pgfgantt}
        \begin{document}
        """
        body = ""
        for a in self.renderDir['Accordion']:
            body +=  a.asLatex()

        postface = r"""
        \end{document}
        """

        outtext = preface + body + postface

        # write file 
        fout = codecs.open(fp, 'w', 'utf-8')
        fout.write (outtext)
        fout.close()

        # run latex
        cwd = os.getcwd()
        os.chdir (workdir)
        retval = subprocess.call (["pdflatex",
                                   '-interaction=batchmode',
                                   "report.tex"]) 
        os.chdir (cwd)


    def fieldEmpty (self, f):
        return ((self.ff.cleaned_data[f] == stellenplanQuery.emptyFieldIndicator) or
                (self.ff.cleaned_data[f] == ''))
        
    @method_decorator(login_required)
    def get(self, request):
        # print request 
        if not request.method == 'GET':
            return  HttpResponseNotFound('<h1>Request type not supported!</h1>')

        if request.GET:
            # es gibt schon eine Anfrage
            self.ff = self.__class__.queryFormClass (request.GET)
            if not self.ff.is_valid():
                print "error", self.__class__.urlTarget + '.html'
                print request 
                return render (request,
                               'stellenplan/' + self.__class__.urlTarget + '.html',
                               {'error_message': 'Bitte berichtigen Sie folgenden Fehler: ',
                               'form': self.ff,
                               'urlTarget': self.__class__.urlTarget,                           
                                   })
            
        else:
            # empty request, neu aufbauen
            # print "empty request!" 
            self.ff = self.__class__.queryFormClass (request.GET)
            self.ff.cleaned_data = {'Von': None,
                                    'Bis': None,
                                    'PDF': False,
                                    }
            self.ff.cleaned_data.update(self.__class__.additionalFields)


        self.renderDir = {
            'form': self.ff,
            'urlTarget': self.__class__.urlTarget,
            }

        ## pp(self.renderDir) 
        ## print self.renderDir['form']
        self.renderDir['Accordion'] = []
        self.constructAccordion (request)

        if self.ff.cleaned_data['PDF']:
            # here trigger the gneration of the PDF file

            self.producePDF()
            self.renderDir['pdf'] = True
            self.renderDir['pdfname'] = 'report.pdf'

        return render (request,
                       "stellenplan/" + self.__class__.urlTarget + ".html",
                       self.renderDir)

        


#################################

    
class qBesetzung (stellenplanQuery):
    """This is just an empty class"""
    urlTarget = 'qBesetzung'
    queryFormClass = BesetzungFilterForm 
    additionalFields = {'Person': stellenplanQuery.emptyFieldIndicator,
                        'Stellennummer': stellenplanQuery.emptyFieldIndicator,
                        }

    def constructAccordion (self, request):

        #  die Besetzungen wie üblich filtern: 
        allBesetzung = Besetzung.objects.all()

        # alle Besetzungen nach Standardfilter 
        qs = standardfilters (allBesetzung, [], self.ff.cleaned_data)


        # print self.ff.cleaned_data
        
        # add a person filter, if that filter was selected
        if not self.fieldEmpty ('Person'): 
            qs = qs.filter (person__personalnummer__exact =
                            self.ff.cleaned_data['Person'])

        if not self.fieldEmpty ('Stellennummer'):
            # print "filtering for ", self.ff.cleaned_data['Stellennummer']
            qs = qs.filter (stelle__stellennummer__exact = 
                            self.ff.cleaned_data['Stellennummer'])
            
        ## # add a fachgebiet filter, if that filer was selected 
        ## if not self.ff.cleaned_data['Fachgebiet'] == self.__class__.emptyFieldIndicator:
        ##     qs = qs.filter (stelle__exact =
        ##                     self.ff.cleaned_data['Fachgebiet'])
        
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
    additionalFields = {'Wertigkeit': stellenplanQuery.emptyFieldIndicator,
                        'Art': stellenplanQuery.emptyFieldIndicator}
    

    def constructAccordion (self, request):

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

        tgWertigkeitOhneZusagen.asAccordion ("Stellen nach Wertigkeit gruppiert, ZUSAGEN abgezogen",
                                             self.renderDir, request)
        
        ########################################
        # und noch mal fast das gleiche, nur jetzt die ZUORDNUNGEN abziehen, 

        qsZuordnung = standardfilters (Zuordnung.objects.all(),
                                    [], self.ff.cleaned_data)
        
        if not self.fieldEmpty('Wertigkeit'):
            qsZuordnung = qsZuordnung.filter (stelle__wertigkeit__exact =
                                              self.ff.cleaned_data['Wertigkeit'])
        tgZuordnungWertigkeit = TimelineGroups(qsZuordnung, 'stelle__wertigkeit')
        

        tgWertigkeitOhneZuordnung = tgWertigkeit.subtract(tgZuordnungWertigkeit)

        tgWertigkeitOhneZuordnung.asAccordion ("Stellen nach Wertigkeit gruppiert, ZURODNUNGEN abgezogen",
                                             self.renderDir, request)
        
        
        ########################################



#########################################################

class qZuordnungen (stellenplanQuery):
    urlTarget = "qZuordnungen"
    queryFormClass = zuordnungenFilterForm
    additionalFields = {'Fachgebiet': stellenplanQuery.emptyFieldIndicator}


    def constructAccordion (self, request):

        # wie ueblich zunaechst eine Uberblick ueber Zusagen, gefiltert 
        qs = standardfilters (Zuordnung.objects.all(),
                              ['Fachgebiet'],
                              self.ff.cleaned_data)
        overviewtab = tables.ZusagenTable (qs)
        RequestConfig (request).configure(overviewtab)

        a = accordion.Accordion ("Zuordnungen insgesamt")
        a.addContent (overviewtab)

        self.renderDir['Accordion'].append(a)

    

#########################################################


class qZusagen (stellenplanQuery):
    """
    Abfragen für Zusagen.
    Filter nach Datum, Fachgebiet, Wertigkeit.
    Zusagen sind durch Zuordnungen unterlegt; interessant sind also Zusagen, für die
    es keine Zuordnungen gibt. 
    """

    urlTarget = "qZusagen"
    queryFormClass = zusagenFilterForm
    additionalFields = {'Wertigkeit': stellenplanQuery.emptyFieldIndicator,
                        'Fachgebiet': stellenplanQuery.emptyFieldIndicator}
    

    def constructAccordion (self, request):

        # wie ueblich zunaechst eine Uberblick ueber Zusagen, gefiltert

        pp(self.ff.cleaned_data)
        
        qs = standardfilters (Zusage.objects.all(),
                              ['Fachgebiet', 'Wertigkeit'],
                              self.ff.cleaned_data)

        print qs
        
        overviewtab = tables.ZusagenTable (qs)
        RequestConfig (request).configure(overviewtab)

        a = accordion.Accordion ("Zusagen insgesamt")
        a.addContent (overviewtab)

        self.renderDir['Accordion'].append(a)


        ########################################


        # Zusagen nach Wertigkeit gruppiert ausgeben
        tgWertigkeit = TimelineGroups(qs, 'wertigkeit')
        tgWertigkeit.asAccordion ("Zusagen, nach Wertigkeit gruppiert",
                                  self.renderDir, request)
        
        ########################################


        ## # Zusagen, nach Fachgebiet gruppiert
        ## # Achtung, das ist sinnlos!
        ## # Man könnte das höchstens mit Personalpunkten gewichten  - TODO!! 
        ## tgFachgebiet = TimelineGroups(qs, 'fachgebiet')
        ## tgFachgebiet.asAccordion ("Zusagen, nach Fachgebiet gruppiert",
        ##                           self.renderDir, request)

        ########################################

        # Zusagen nach Wertigkeit gruppiert ausgeben - davon die entsprechenden
        # gruppierten ZuORDNUNGEN abziehen

        qsZuordnung = standardfilters (Zuordnung.objects.all(),
                                       ['Fachgebiet'],
                                       self.ff.cleaned_data)
        if not self.fieldEmpty ('Wertigkeit'):
            qsZuordnung = qsZuordnung.filter (stelle__wertigkeit__exact =
                                              self.ff.cleaned_data['Wertigkeit'])
        tgZuordnungWertigkeit = TimelineGroups(qsZuordnung, 'stelle__wertigkeit')
        
        tgZusagenOhneZuordnung = tgWertigkeit.subtract(tgZuordnungWertigkeit)
        tgZusagenOhneZuordnung.asAccordion ("Offene Zusagen (Zuordnungen sind abgezogen), nach Wertigkeit gruppiert",
                                            self.renderDir, request)
    



##############################################################
