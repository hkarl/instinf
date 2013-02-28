# -*- coding: utf-8 -*-

from datetime import timedelta 
import django_tables2
import tables
import copy
import datetime
import re
from pprint import pprint as pp 

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

    def start (self):
        return min (self.m.keys())
    
    def stop (self):
        return max (self.m.keys())


    def aslist (self, cols={}):
        r = []
        for d in sorted(self.m.keys()):
            rr = {}
            rr.update(cols)
            rr.update( {'Datum': d, 'Prozent': self.m[d]})
            r.append(rr)

        return r

    def aslatex (self,cols={}):
        r = []
        return '\\\\ \n'.join([' & ' + d.__str__() + ' & ' + self.m[d].__str__()
                               for  d in sorted(self.m.keys())])

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

    def asHighchartValue (self):
        v = []
        for k in sorted(self.m.keys()):
            # print k, type(k)
            v.append ("[Date.UTC(%d, %d, %d), %d]" %
                      (k.year, k.month, k.day, self.m[k]))
            
        return ",\n".join(v)
    
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
        # print "dumping a grouped timeline"
        for k, v in self.tlg.iteritems():
            # print k
            v.dump()

    def asTable (self, request=None):

        # construct results in suitable fashion
        r = []
        for k,v in self.tlg.iteritems():
            r.extend(v.aslist({'Gruppe': k}))

        #print r
        
        tbl = tables.GruppenTable(r)
        django_tables2.RequestConfig(request).configure(tbl)

        return tbl
    
    def asLatexTable (self):

        res = '\\begin{tabular}{ccc}\n \\toprule '
        res += 'Gruppierung & Datum & Prozent \\\\ \n \\midrule '
        res += ' \\\\ \\midrule  \midrule \n'.join([ k + '\\\\  \\midrule\n' + v.aslatex({'Gruppe': k})
                for k,v in  self.tlg.iteritems()])

        res += '\\\\ \\bottomrule \n \\end{tabular}'
        # print res 
        # print "----"
        return res


    def asLatexGantt (self):
        "timelinegroup als latex GRafik ist noch nicht implementiert!!"
        res = r""""
        \begin{ganttchart}{12}
        [vgrid,hgrid,
         x unit=0.371cm, y unit chart = 0.75cm,
         title label font={\footnotesize},
         bar height = 0.55,
         bar top shift = 0.225,
         inline,
         milestone label font=\color{black}\small,
         milestone label inline anchor={right=.1cm},
        bar label inline anchor={anchor=west}, bar label font=\small,
        link={-latex, rounded corners=1ex, thick}]
        """
        

        # find out how many quarters there are
        # print "asLatexGantt" 
        # pp([(k, v.stop() - v.start()) for k,v in self.tlg.iteritems()])
        

        res += r"""
        \end{ganttchart}
        """

        return res 



    def asHighchart (self, tag):

        print "-----\nHighchart" 
        series = []
        yaxis = []
        top = 100
        count = 0
        height = 200
        margin = 50 

        for k,v in self.tlg.iteritems():

            yaxis.append ("""
                {
                title: {text: '%s'},
                height: %d,
                top: %d,
                offset: 30
                }
            """ % (k, height, top))

            # Alternativer Versuch: 
            # """ % (k, top))
            top += height + margin 
            
            series.append("""            {
              name: '%s',
              type: 'line',
              data: [ %s ],
              yAxis: %d,
              step: true 
            }""" % (k, v.asHighchartValue(), count))

            count += 1 
        # print ",\n".join(series)

        totalheight = top + 2*margin  

        r = """
        <script  type="text/javascript">
       $(function() {
		new Highcharts.StockChart({
		    chart: {
		        renderTo: '%s',
                        height: %d
		    },

		    rangeSelector: {
		        selected: 1
		    },

                    yAxis: [%s],

		    title: {
		        text: 'Zeitverlauf'
		    },
                    xAxis: {
                        ordinal: false
		    },		    
		    series: [%s]
                    });
        });
        </script>
        """ % (tag, totalheight, 
               ",\n".join(yaxis), ",\n".join(series))

        print r 
        return r 

    
    def asjGantt (self, tag):
        r = """
        <script>
        $(function() {
          "use strict";
          $(".%s").gantt({
            source: [{""" % tag

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
        ac.addtab ("Graph", self.asHighchart(key+"-HS"))
        ac.addtab ("Tabelle", self.asTable(request), latex=self.asLatexTable())
        ac.addtab ("Gantt", self.asjGantt(key), latex=self.asLatexGantt())
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
    
