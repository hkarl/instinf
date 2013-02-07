import re 

class Accordion:
    """This class stores the title of an accordion entry, as well as a list of
    tabs with title and content. """

    def __init__ (self, t):
        self.title  = t
        self.key = re.sub (r'[^a-zA-Z0-9]+', '', t)
        self.content = []
        self.mainContent = None
        
    def addtab (self, title, html):
        self.content.append ({
            't': title,
            'c': html, 
            })
        
    def addContent (self, c):
        self.mainContent = c 

    def __repr__ (self):
        return self.title 
