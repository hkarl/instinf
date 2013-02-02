# -*- coding: utf-8 -*-

from datetime import timedelta 
import django_tables2
import tables


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

    def subtract (self, minuend):
        """Create a NEW tg, subtract the minuend, and return the newly created tg"""

        tg = TimelineGroups()
        tg.tlg = self.tlg

        # stelle sicher, dass alle im Minuenden vorkommenden keys auch im REsultat vorkommen
        for k in minuend.tlg.keys():
            if not k in tg.tlg:
                tg.tlg[k] = Timeline()

            # und dann abziehen:
            tg.tlg[k].addTL (minuend.tlg[k], -1)
 
        return tg 
        
