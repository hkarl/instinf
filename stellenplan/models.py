# -*- coding: utf-8 -*-
from django.db import models


# Models for Stellenplan for Informatik für  Institut 


def monatsinterval (x):
    try:
        return x.von.strftime("%Y-%m-%d") + " - " + x.bis.strftime("%Y-%m-%d")
    except:
        return ""
    
class Fachgebiet(models.Model):
    kuerzel = models.CharField("Fachgebietskürzel",
                              max_length=10,
                              help_text="Ein Kürzel für das Fachgebiet, meist einige Buchstaben.",
                              primary_key = True,
                              unique = True,
                              )
    fgname = models.CharField ("Fachgebietsname",
                              max_length=50,
                              help_text="Der offizielle Name des Fachgebietes",
                              unique=True,
                              )
    von = models.DateField ("Einrichtungsdatum",
                      help_text="Wann wurde das Fachgebiet eingerichtet?")
    bis = models.DateField ("Auflösungsdatum",
                      help_text="Wann wird das Fachgebiet aufgelöst?")
    kostenstelle = models.DecimalField ("Abrechnungsobjekt",
                                       max_digits=10,
                                       decimal_places=0,
                                       blank=True,
                                       help_text="Abrechnungsobjekt des Fachgebiets")
    annmerkung = models.TextField ("Anmerkungen",
                             help_text="Beliebige Anmerkungen.",
                             blank=True,
                             )
    lastmodified = models.DateField ("Letzte Änderung",
                               help_text="Wann wurde die letzte Änderung vorgenommen? Wird automatisch gesetzt.",
                               auto_now=True)

    def __unicode__ (self):
        return self.kuerzel

##########################################

    
class Stellenart (models.Model):
    stellenart = models.CharField("Stellenart",
                                  max_length=20,
                                  help_text="Welche Stellenarten unterscheiden wir?",
                                  primary_key=True,
                                  unique=True,
                                  )
    annmerkung = models.TextField ("Anmerkungen",
                             help_text="Beliebige Anmerkungen.",
                             blank=True,
                             )
    lastmodified = models.DateField ("Letzte Änderung",
                               help_text="Wann wurde die letzte Änderung vorgenommen? Wird automatisch gesetzt.",
                               auto_now=True)

    def __unicode__ (self):
        return self.stellenart 

##########################################


class Stellenwertigkeit (models.Model):
    wertigkeit = models.CharField ("Wertigkeit",
                                   max_length=10,
                                   help_text = "Welche Wertigkeiten für Stellen existieren?",
                                   primary_key=True,
                                   unique=True,
                                   )
    personalpunkte = models.DecimalField ("Personalpunkte",
                                          max_digits=5,
                                          decimal_places=2, 
                                          help_text="Wieviele Personalpunkte entsprechen einer solchen Wertigkeit?",
        )
    annmerkung = models.TextField ("Anmerkungen",
                             help_text="Beliebige Anmerkungen.",
                             blank=True,
                             )
    lastmodified = models.DateField ("Letzte Änderung",
                               help_text="Wann wurde die letzte Änderung vorgenommen? Wird automatisch gesetzt.",
                               auto_now=True)

    def __unicode__ (self):
        return self.wertigkeit 


##########################################

class Stelle (models.Model):
    stellennummer = models.DecimalField ("Stellennummer",
                                         help_text ="Eindeutige Stellennummer",
                                         unique = True,
                                         primary_key = True,
                                         max_digits=5,
                                         decimal_places=0,
                                         )
    wertigkeit = models.ForeignKey ('Stellenwertigkeit',
                                    help_text= "Wertigkeit der Stelle?")
    art = models.ForeignKey ('Stellenart',
                             help_text="Welcher Art ist diese Stelle? (Land, ...)")
                             
    von = models.DateField ("Stellenbeginn",
                      help_text="Ab wann ist die Stelle verfügbar?")
    bis = models.DateField ("Stellenenden",
                      help_text="Wann endet die Verfügbarkeit der Stelle?")
    prozent = models.DecimalField ("Prozent",
                                   max_digits=3,
                                   decimal_places=0,
                                   help_text="Wieviel Prozent der VOLLEN Stelle?",
                                   )
    annmerkung = models.TextField ("Anmerkungen",
                             help_text="Beliebige Anmerkungen.",
                             blank=True,
                             )
    lastmodified = models.DateField ("Letzte Änderung",
                               help_text="Wann wurde die letzte Änderung vorgenommen? Wird automatisch gesetzt.",
                               auto_now=True)

    def __unicode__ (self):
        return (unicode(self.stellennummer)  +
                " (" + self.wertigkeit.wertigkeit + ", " + self.art.stellenart + ", " +
                 monatsinterval(self) + ")" 
                )

##########################################

class Person (models.Model):
    personalnummer = models.DecimalField ("Personalnummer",
                                          help_text = "Personalnummer der Person",
                                          primary_key = True,
                                          unique = True,
                                          max_digits=10,
                                          decimal_places=0,)
    name = models.CharField ("Nachname",
                             help_text="Nachname",
                             max_length=50,
                             )
    vorname = models.CharField ("Vorname",
                             help_text="Vorname",
                             max_length=50,
                             )
    wertigkeit = models.ForeignKey ('Stellenwertigkeit',
                                    help_text="Welche Wertigkeit hat der Vertrag?",
        to_field="wertigkeit")
    von = models.DateField ("Einstellung",
                      help_text="Wann wurde die Person (auf dieser Wertigkeit) eingestellt?")
    bis = models.DateField ("Ende",
                      help_text="Wann endet das Arbeitsverhältnis bzw. diese Wertigkeit?")
    prozent = models.DecimalField ("Prozent",
                                   max_digits=3,
                                   decimal_places=0,
                                   help_text="Wieviel Prozent der VOLLEN Arbeitszeit?",
                                   )
    annmerkung = models.TextField ("Anmerkungen",
                             help_text="Beliebige Anmerkungen.",
                             blank=True,
                             )
    lastmodified = models.DateField ("Letzte Änderung",
                               help_text="Wann wurde die letzte Änderung vorgenommen? Wird automatisch gesetzt.",
                               auto_now=True)

    def __unicode__ (self):
        return self.name + ", " + self.vorname + " (" + unicode(self.personalnummer) +  ", " + monatsinterval(self) +  ")"

##########################################


class Zusage (models.Model):
    fachgebiet = models.ForeignKey ('Fachgebiet',
                                    help_text = "Welchem Fachgebiet wird die Zusage gemacht?")
    wertigkeit = models.ForeignKey ('Stellenwertigkeit',
                                    help_text="Welche Wertigkeit hat die zugesagte Stelle?")
    prozent = models.DecimalField ("Prozent",
                                   max_digits=3,
                                   decimal_places=0,
                                   help_text="Wieviel Prozent der VOLLEN Stellenwertigkeit werden zugesagt?",
                                   )
    von = models.DateField ("Zusagenbeginn",
                      help_text="Ab wann gilt die Zusage?")
    bis = models.DateField ("Zusagenende",
                      help_text="Bis wann gilt die Zusage?")
    annmerkung = models.TextField ("Anmerkungen",
                             help_text="Beliebige Anmerkungen.",
                             blank=True,
                             )
    lastmodified = models.DateField ("Letzte Änderung",
                               help_text="Wann wurde die letzte Änderung vorgenommen? Wird automatisch gesetzt.",
                               auto_now=True)

    def __unicode__ (self):
        return self.wertigkeit.wertigkeit + "@" + self.fachgebiet.kuerzel + " (" + unicode(self.prozent) + ", " + monatsinterval(self) + ")"

##########################################


class Zuordnung (models.Model):
    fachgebiet = models.ForeignKey ('Fachgebiet',
                                    help_text = "Welchem Fachgebiet wird die Stelle zugeordnet?")
    stelle = models.ForeignKey ('Stelle',
                                help_text="Welche Stelle wird zugeordnet?")
    prozent = models.DecimalField ("Prozent",
                                   max_digits=3,
                                   decimal_places=0,
                                   help_text="Wieviel Prozent der VOLLEN Stellenwertigkeit werden zugeordnet?",
                                   )
    von = models.DateField ("Zuordnungsbeginn",
                      help_text="Ab wann ist die Stelle dem Fachgebiet zugeordnet?")
    bis = models.DateField ("Zuordnungsende",
                      help_text="Bis wann gil die Zuordnung?")
    annmerkung = models.TextField ("Anmerkungen",
                             help_text="Beliebige Anmerkungen.",
                             blank=True,
                             )
    lastmodified = models.DateField ("Letzte Änderung",
                               help_text="Wann wurde die letzte Änderung vorgenommen? Wird automatisch gesetzt.",
                               auto_now=True)

    def __unicode__ (self):
        return unicode(self.stelle.stellennummer) + "@" + self.fachgebiet.kuerzel + " (" + unicode(self.prozent) + ", " + monatsinterval(self) + ")"

    
##########################################

class Besetzung (models.Model):
    person = models.ForeignKey ('Person',
                                help_text ="Welche Person wird auf eine Stelle besetzt?")
    stelle = models.ForeignKey ('Stelle',
                                help_text="Welche Stelle wird besetzt?")
    prozent = models.DecimalField ("Prozent",
                                   max_digits=3,
                                   decimal_places=0,
                                   help_text="Wieviel Prozent der VOLLEN Stellenwertigkeit werden zugeordnet?",
                                   )
    von = models.DateField ("Besetzungsbeginn",
                      help_text="Ab wann ist die Stelle mit der Person besetzt?")
    bis = models.DateField ("Besetzungsende",
                      help_text="Bis wann ist die Stelle besetzt?")
    pseudo = models.BooleanField ("Pseudobesetzung?",
                                  help_text="Falls diese Stelle nur scheinbar mit NN besetzt wird, dieses Feld anklicken.",
                                  default=False,
                                  )
                                  
    annmerkung = models.TextField ("Anmerkungen",
                             help_text="Beliebige Anmerkungen.",
                             blank=True,
                             )
    lastmodified = models.DateField ("Letzte Änderung",
                               help_text="Wann wurde die letzte Änderung vorgenommen? Wird automatisch gesetzt.",
                               auto_now=True)

    def __unicode__ (self):
        return self.person.name + "@" + unicode(self.stelle.stellennummer)
