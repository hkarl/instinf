import re 

class Accordion:
    """This class stores the title of an accordion entry, as well as a list of
    tabs with title and content. """

    def __init__ (self, t):
        self.title  = t
        self.key = re.sub (r'[^a-zA-Z0-9]+', '', t)
        self.content = []
        self.mainContent = None
        
    def addtab (self, title, html, latex=None):
        self.content.append ({
            't': title,
            'c': html,
            'l': latex if latex else "",
            })
        
    def addContent (self, c):
        self.mainContent = c
        try: 
            self.mainLatex = c.aslatex()
        except:
            self.mainLatex = "" 
            
    def asLatex (self):
        r = r"\section{" + self.title + "}\n"
        if self.mainContent:
            r += self.mainLatex
        else:
            for e in self.content:
                r += r"\subsection{"+ e['t']  + "}\n"
                r += e['l']
                r += "\n\n"

        r += "\n\n"
        return r

    def __repr__ (self):
        return self.title 
