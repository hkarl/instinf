# -*- coding: utf-8 -*-

from datetime import timedelta 
import django_tables2
import tables
import copy
import datetime
import re

from accordion import Accordion


def unix_time(dt):
    epoch = datetime.datetime.utcfromtimestamp(0).date()
    delta = dt - epoch
    return delta.total_seconds()

def unix_time_millis(dt):
    return unix_time(dt) * 1000.0



class Timeline:
    """A class to store a timeline: maps points in time to integer values.
    Can add intervals with a certain value.
    Initial value given during construction.
    """

    initialValue  = 0
    
    def __init__ (self, initv = 0, qs = None):
        self.initialValue = initv
        self.m = {}

        
    def dump (self):
        for d in sorted(self.m.keys()):
            print d, self.m[d]

    def aslist (self, cols={}):
        r = []
        for d in sorted(self.m.keys()):
            rr = {}
            rr.update(cols)
            rr.update( {'Datum': d, 'Prozent': self.m[d]})
            r.append(rr)

        return r 

    def ensure (self, d):
        """Ensure that a given date is a key in the dictionary.
        Use the youngest predecusor's value as value for this new one as well. 
        Makes insertion of intervals easier.
        """
        if not self.m:
            self.m[d] = self.initialValue
        elif d in self.m:
            return 
        elif d < min(self.m.keys()):
            self.m[d] = self.initialValue
        else:
            # find the newest date younger than the one to be inserted
            # use that date's value as the initial value for the new date
            x = max([dt for dt in self.m.keys() if dt < d])
            self.m[d] = self.m[x]
            
    def add (self, v, b, p):
        """Insert an interval into the dictionary. Add the (possibly negative)
        percentage to all the intermediate dates. """
        
        self.ensure (v)
        self.ensure (b + timedelta(1))

        relevantdates = [dt for dt in self.m.keys()
                         if ((v <= dt) and (dt <= b))]
        for r in relevantdates:
            self.m[r] += p 

    def addTL (self, tl, vorzeichen):
        """Von self einen andere timeline abziehen."""

        datelist = sorted(tl.m.keys())
        for i in range(0,len(datelist)-1):
            self.add(datelist[i], datelist[i+1], vorzeichen*tl.m[datelist[i]])

    def asjGanttValue (self):
        kk = sorted(self.m.keys())
        v = []
        for i in range(0, len(kk)-1):
            # print kk[i], kk[i+1], self.m[kk[i]]
            v.append( '''
            from: "/Date(%d)/",
            to: "/Date(%d)/",
            label: "%s",
            customClass: "gantt-II%d"
            ''' % (unix_time_millis(kk[i]),
                   unix_time_millis(kk[i+1]),
                   self.m[kk[i]]/100,
                   min(max(self.m[kk[i]]/100, -10), 10)))

        return "[{" + "},\n{".join(v) + "}]"
    
class TimelineGroups ():
    """ Grouping a queryset along a given column, producing one timeline for each
    value in that column.
    Internal structure: a map, keys are the column values, values are timeline instances. """

    def __init__ (self, qs=None, column=None):
        self.tlg = {}
        if column:
            filterString = column + '__' + 'exact'
            ## print filterString 
            
            columnvalues = qs.values(column).distinct().all()
            for c in columnvalues:
                ## print 'g', g
                ## print 'dict', {filterString: g[column]}
                qsColumned = qs.filter(**{filterString: c[column]})
                self.tlg[c[column]] = self.TLfromQueryset (qsColumned)
        else:
            if qs:
                self.tlg[""] = self.TLfromQueryset(qs)

    def TLfromQueryset (self, qs):
        tl = Timeline()
        for x in qs.all():
            tl.add(x.von, x.bis, x.prozent)
        return tl
    
    def dump (self):
        print "dumping a grouped timeline"
        for k, v in self.tlg.iteritems():
            print k
            v.dump()

    def asTable (self, request=None):

        # construct results in suitable fashion
        r = []
        for k,v in self.tlg.iteritems():
            r.extend(v.aslist({'Gruppe': k}))

        # print r
        
        tbl = tables.GruppenTable(r)
        django_tables2.RequestConfig(request).configure(tbl)

        return tbl

    def asjGantt (self, tag):
        r = """
        <script>
        $(function() {
          "use strict";
          $(".%s").gantt({
            source: [{
        """ % tag

        rr = []
        # iterate over the individual timelines, gives one chart entry each
        for k, v in self.tlg.iteritems():
            # print k,  v.asjGanttValue()
            rr.append('''
            name: "%s",
            values: %s
            ''' % (k, v.asjGanttValue()))

        r += "},{".join (rr)
        
        r += """
        }],
        navigate: "scroll",
        scale: "months",
        maxScale: "years",
        minScale: "months",
        itemsPerPage: 10,
        onRender: function() {
        if (window.console && typeof console.log === "function") {
        console.log("chart rendered");
        }
        }        
        });
        });
        </script>
        """

        # print r
        return r 

    def asAccordion (self, title, d, request):
        """
        Turn this timeline group into an accordion entry with two tabs: table and gantt.
        Add them to corresponding entires in the dictionary. 
        """

        if 'Accordion' not in d:
            d['Accordion'] = []

        key = re.sub (r'[^a-zA-Z0-9]+', '', title)
        ac =  Accordion(title)
        ac.addtab ("Tabelle", self.asTable(request))
        ac.addtab ("Gantt", self.asjGantt(key))
        d['Accordion'].append(ac) 

        ## key = re.sub (r'[^a-zA-Z0-9]+', '', title)
        ## d['Accordion'].append ({
        ##     'title': title,
        ##     'key': key, 
        ##     'content' : [ {'t': 'Tabelle',
        ##                    'c': self.asTable(request),},
        ##                    {'t': 'Gantt',
        ##                     'c': self.asjGantt(key)}],
        ##     })
            

        


    def subtract (self, minuend):
        """Create a NEW tg, subtract the minuend, and return the newly created tg"""

        # tg = TimelineGroups()
        # tg.tlg = self.tlg
        tg = copy.deepcopy(self) 

        # stelle sicher, dass alle im Minuenden vorkommenden keys auch im REsultat vorkommen
        for k in minuend.tlg.keys():
            if not k in tg.tlg:
                tg.tlg[k] = Timeline()

            # und dann abziehen:
            tg.tlg[k].addTL (minuend.tlg[k], -1)
 
        return tg 
        
## Example for the script:

    ## <script>

    ##     	$(function() {

    ##     		"use strict";

    ##     		$(".gantt").gantt({
    ##     			source: [{
    ##     				name: "Sprint 0",
    ##     				desc: "Analysis",
    ##     				values: [{
    ##     					from: "/Date(1320192000000)/",
    ##     					to: "/Date(1322401600000)/",
    ##     					label: "Requirement Gathering", 
    ##     					customClass: "ganttRed"
    ##     				}]
    ##     			},{
    ##     				name: " ",
    ##     				desc: "Scoping",
    ##     				values: [{
    ##     					from: "/Date(1322611200000)/",
    ##     					to: "/Date(1323302400000)/",
    ##     					label: "Scoping", 
    ##     					customClass: "ganttRed"
    ##     				}]
    ##     			},{
    ##     				name: "Sprint 1",
    ##     				desc: "Development",
    ##     				values: [{
    ##     					from: "/Date(1323802400000)/",
    ##     					to: "/Date(1325685200000)/",
    ##     					label: "Development", 
    ##     					customClass: "ganttGreen"
    ##     				}]
    ##     			},{
    ##     				name: " ",
    ##     				desc: "Showcasing",
    ##     				values: [{
    ##     					from: "/Date(1325685200000)/",
    ##     					to: "/Date(1325695200000)/",
    ##     					label: "Showcasing", 
    ##     					customClass: "ganttBlue"
    ##     				}]
    ##     			},{
    ##     				name: "Sprint 2",
    ##     				desc: "Development",
    ##     				values: [{
    ##     					from: "/Date(1326785200000)/",
    ##     					to: "/Date(1325785200000)/",
    ##     					label: "Development", 
    ##     					customClass: "ganttGreen"
    ##     				}]
    ##     			},{
    ##     				name: " ",
    ##     				desc: "Showcasing",
    ##     				values: [{
    ##     					from: "/Date(1328785200000)/",
    ##     					to: "/Date(1328905200000)/",
    ##     					label: "Showcasing", 
    ##     					customClass: "ganttBlue"
    ##     				}]
    ##     			},{
    ##     				name: "Release Stage",
    ##     				desc: "Training",
    ##     				values: [{
    ##     					from: "/Date(1330011200000)/",
    ##     					to: "/Date(1336611200000)/",
    ##     					label: "Training", 
    ##     					customClass: "ganttOrange"
    ##     				}]
    ##     			},{
    ##     				name: " ",
    ##     				desc: "Deployment",
    ##     				values: [{
    ##     					from: "/Date(1336611200000)/",
    ##     					to: "/Date(1338711200000)/",
    ##     					label: "Deployment", 
    ##     					customClass: "ganttOrange"
    ##     				}]
    ##     			},{
    ##     				name: " ",
    ##     				desc: "Warranty Period",
    ##     				values: [{
    ##     					from: "/Date(1336611200000)/",
    ##     					to: "/Date(1349711200000)/",
    ##     					label: "Warranty Period", 
    ##     					customClass: "ganttOrange"
    ##     				}]
    ##     			}],
    ##     			navigate: "scroll",
    ##     			scale: "weeks",
    ##     			maxScale: "months",
    ##     			minScale: "days",
    ##     			itemsPerPage: 10,
    ##     			onRender: function() {
    ##     				if (window.console && typeof console.log === "function") {
    ##     					console.log("chart rendered");
    ##     				}
    ##     			}
    ##     		});


    ##     	});

    ## </script>
    
