# -*- coding: utf-8 -*-



# generic python 
from pprint import pprint as pp 
import datetime 


# django imports 
from django.views.generic import View
from django.shortcuts import render
from django.contrib.contenttypes.models  import ContentType 
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core import urlresolvers


# from this app: 
from stellenplanForms import * 
from timeline import Timeline 

###########################################################


class konsistenz (View):

    def check_overlap (self, qs, col):
        """Given a queryset for a table with von and bis values, do these intervales overlap?
        """

        intervals = sorted([(q.von, q.bis, q.pk) for q in qs], key = lambda x: x[0])
        # print intervals
        violationList = []
        for i in range(len(intervals)-1):
            if (intervals[i][1] >= intervals[i+1][0]):
                violationList.append ((intervals[i][2],
                                       intervals[i+1][2],
                                    ))

        return violationList 
        
    @method_decorator (login_required)
    def get (self, request):

        ##############################
        # check overlaps of intervals, uniqueness identified via the column : 
        overlapchecks = [ (Person, 'personalnummer'),
                          (Fachgebiet, 'kuerzel'),
                          (Stelle, 'stellennummer'),
                          (Zuordnung, 'stelle'), 
                          (Besetzung, 'stelle'), 
                        ]
        overlapmsg = []

        for o in overlapchecks:
            # print o[0]
            for k in o[0].objects.values(o[1]).distinct().all():

                qs = o[0].objects.filter (**{ o[1] + '__exact':   k[o[1]]})
                violationList= self.check_overlap (qs, o[1])

                
                if violationList:

                    violationURLs =  [ (urlresolvers.reverse ('admin:stellenplan_' +
                                                              o[0].__name__.lower()  + '_change', args=(v[0],)),
                                        urlresolvers.reverse ('admin:stellenplan_' +
                                                              o[0].__name__.lower()  + '_change', args=(v[1],)),
                                                              
                                        qs.get(id=v[0]).__unicode__(),
                                        qs.get(id=v[1]).__unicode__(),
                                        )
                                        for v in violationList ]

                    overlapmsg.append({'module_name': o[0].__name__,
                                       'field': o[1].capitalize(),
                                       'violationUrls': violationURLs})
        #print overlapmsg 

        ##############################

        # Konsistenz der Verknuepfungen: Teilmengen der intervalkle müssen eingehalten werden 
        # Klasse: von -bis muss Teilintervall des foreign keys sein 

        teilintervallbeziehungen = [(Zusage, "fachgebiet"),
                                    (Zuordnung, "fachgebiet"),
                                    (Zuordnung, "stelle"),
                                    (Besetzung, "person"),
                                    (Besetzung, "stelle"),
                                    ]
        
                
        teilintervallkonflikte =  filter (lambda x: x[2],
                       [(tib[0].__name__, tib[1].capitalize(),
                  [ ( urlresolvers.reverse ('admin:stellenplan_' +
                                            tib[0].__name__.lower() + '_change',
                                            args = (entry.pk,)),
                       urlresolvers.reverse ('admin:stellenplan_' +
                                             getattr (entry, tib[1]).__class__.__name__.lower() + '_change',
                                             args = (getattr (entry, tib[1]).pk,)),                                                        entry.__unicode__(),
                       getattr (entry, tib[1]).__unicode__()
                      )
                      for entry in tib[0].objects.all()
                      if not (( entry.von >= getattr (entry, tib[1]).von ) and
                              ( entry.von <= getattr (entry, tib[1]).bis ) and
                              ( entry.bis >= getattr (entry, tib[1]).von ) and
                              ( entry.bis <= getattr (entry, tib[1]).bis ) )
                      ])
                for tib in teilintervallbeziehungen ]
                )



        ##############################


        # Wurden stellen mehrfach besetzt? use following backwords:
        # https://docs.djangoproject.com/en/dev/topics/db/queries/#backwards-related-objects


        besetzungStelleKonflikt = []
        zuordnungStelleKonflikt = []

        for stelle in Stelle.objects.all():

            ## print "----" 
            ## print "Stelle: ", stelle
            
            tlBesetzung = Timeline()
            besetzungenDieserStelle = stelle.besetzung_set.all()
            for bes in besetzungenDieserStelle: 
                tlBesetzung.add (bes.von, bes.bis, bes.prozent)


            tlZuordnung = Timeline()
            zuordnungenDieserStelle = stelle.zuordnung_set.all()
            for zu in zuordnungenDieserStelle: 
                tlZuordnung.add (zu.von, zu.bis, zu.prozent)


            conflictsBesetzung = tlBesetzung.aboveThreshold(stelle.prozent)
            conflictsZuordnung = tlZuordnung.aboveThreshold(stelle.prozent)

            ## print "Conflicts Zuordnung" 
            ## pp (conflictsZuordnung)
            ## tlZuordnung.dump()

            if conflictsBesetzung:
                tmp = []
                for c in conflictsBesetzung:
                    tmp.append ((c[0], c[1], c[2],
                                 [(b.__unicode__(),
                                   urlresolvers.reverse ('admin:stellenplan_besetzung_change',
                                                         args = (b.pk,))
                                   ) for b in 
                                  besetzungenDieserStelle.exclude(bis__lt = c[0]).exclude(von__gt = c[1]).all()
                                 ]))

                besetzungStelleKonflikt.append((stelle,
                                                urlresolvers.reverse ('admin:stellenplan_stelle_change',
                                                                      args = (stelle.pk,)),
                                                tmp))


            if conflictsZuordnung:
                tmp = []
                for c in conflictsZuordnung:
                    tmp.append ((c[0], c[1], c[2],
                                 [(b.__unicode__(),
                                   urlresolvers.reverse ('admin:stellenplan_zuordnung_change',
                                                         args = (b.pk,))
                                   ) for b in 
                                  zuordnungenDieserStelle.exclude(bis__lt = c[0]).exclude(von__gt = c[1]).all()
                                 ]))

                zuordnungStelleKonflikt.append((stelle,
                                                urlresolvers.reverse ('admin:stellenplan_stelle_change',
                                                                      args = (stelle.pk,)),
                                                tmp))


        ## print "----" 
        ## pp(besetzungStelleKonflikt)
        ## pp(zuordnungStelleKonflikt)

        ##############################

        # welche Personen wurden noch nicht besetzt, sind also nicht finanziert?
        # gruppiere Personen nach Personalnummer, bilde jeweils eine Timeline, und ziehe davon die Besetzungstimeline ab, die für diese Personalnummer entsteht
                
        personUnbesetzt = []
        
        for pGrouped in Person.objects.values('personalnummer').distinct().all():
            # print pGrouped

            pTl = Timeline ()
            bTl = Timeline ()
            
            for p in Person.objects.all().filter(personalnummer__exact = pGrouped['personalnummer']):
                #  print p
                pTl.add (p.von, p.bis, p.prozent)

            for b in Besetzung.objects.all().filter(person__personalnummer__exact = pGrouped['personalnummer']):
                # print b
                bTl.add (b.von, b.bis, b.prozent)

            pTl.addTL (bTl, -1)
            
            fehlendeBesetzung = pTl.aboveThreshold(0)

            if fehlendeBesetzung:
                # pp(fehlendeBesetzung)

                personUnbesetzt.append({
                    'person': [ {'name': p.__unicode__(),
                                 'url': urlresolvers.reverse ('admin:stellenplan_person_change',
                                                              args = (p.pk,))}
                                 for p in
                                 Person.objects.all().filter(personalnummer__exact = pGrouped['personalnummer'])],
                    'intervalle': fehlendeBesetzung,
                    'besetzung': [ {'name': b.__unicode__(),
                                    'url': urlresolvers.reverse ('admin:stellenplan_besetzung_change',
                                                              args = (b.pk,))} 
                                    for b in
                                    Besetzung.objects.all().filter(person__personalnummer__exact = pGrouped['personalnummer'])]
                    })

        # pp (personUnbesetzt)

        ##############################

        # Wurden Personen auf Stellen besetzt, die eine geringere Wertigkeit hat als die Person?
        # Was heisst  "geringer", weniger Personalpunkte? 

        wertigkeitNichtAusreichend = [ {'besetzung':  b.__unicode__(),
                                        'url': urlresolvers.reverse ('admin:stellenplan_besetzung_change',
                                                    args = (b.pk,))
                                        }
                                      for b in Besetzung.objects.all()
                                      if (b.person.wertigkeit.personalpunkte >
                                          b.stelle.wertigkeit.personalpunkte )]
        ## for b in Besetzung.objects.all():
        ##     print b
        ##     print b.person.wertigkeit.personalpunkte
        ##     print b.stelle.wertigkeit.personalpunkte 
            

	#  pp(wertigkeitNichtAusreichend)

        ##############################
        
        return render (request,
                       'stellenplan/konsistenz.html',
                        {'overlap': overlapmsg,
                         'teilintervallkonflikte': teilintervallkonflikte,
                         'besetzungStelleKonflikt': besetzungStelleKonflikt, 
                         'zuordnungStelleKonflikt': zuordnungStelleKonflikt,
                         'personUnbesetzt': personUnbesetzt,
                         'wertigkeitNichtAusreichend': wertigkeitNichtAusreichend, 
                        })
    
