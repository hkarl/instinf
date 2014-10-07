# -*- coding: utf-8 -*-

"""
Stellenplan models: Persons, Groups, Contracts

* :class:`Fachgebiet`: A research group
* :class:`Stellenart`: Which types of Stellen exist?
* :class:`Stellenwertigkeit`: Which types of Stelle do exist? (E13, ...)
* :class:`StellenwertigkeitIntervall`: How much is a particular Wertigkeit
worth at particular points in time?
* :class:`Stelle`: when does a particular Stelle, of which particular type,
exist?
* :class:`Person`: a real person
* :class:`PersonZusage`: Which promises in Wertigkeit have been made to a
Person, for which time?
* :class:`Zusage`: A promise aber a Stelle to a Fachgebiet, for a
particular time
* :class:`Zuordnung`: Which Stelle is at the disposal of which Fachgebiet,
for which time?
* :class:`Besetzung`: Which Person occupies which Stelle, when,
at how much percent?
"""


from django.db import models


def monatsinterval(x):
    try:
        return x.von.strftime("%Y-%m-%d") + " - " + x.bis.strftime("%Y-%m-%d")
    except:
        return ""


class Fachgebiet(models.Model):
    """Fachgebiet: Name, short acronym, when did it start, when will it
    regularly end? (Use pension date of head of group, or termination
    date for a limited contract. Kostenstelle desribes the
    Restemittel-Konto.
    """

    kuerzel = models.CharField("Fachgebietskürzel",
                               max_length=10,
                               help_text="Ein Kürzel für das Fachgebiet,"
                               " meist einige Buchstaben.",
                               primary_key=False,
                               unique=False,
                               )
    fgname = models.CharField("Fachgebietsname",
                              max_length=50,
                              help_text="Der offizielle Name des Fachgebietes",
                              unique=False,
                              )
    von = models.DateField("Einrichtungsdatum",
                           help_text="Wann wurde das Fachgebiet eingerichtet?")
    bis = models.DateField("Auflösungsdatum",
                           help_text="Wann wird das Fachgebiet aufgelöst?")
    kostenstelle = models.DecimalField(
        "Abrechnungsobjekt",
        max_digits=10,
        decimal_places=0,
        help_text="Abrechnungsobjekt des Fachgebiets")
    annmerkung = models.TextField("Anmerkungen",
                                  help_text="Beliebige Anmerkungen.",
                                  blank=True,
    )
    lastmodified = models.DateField(
        "Letzte Änderung",
        help_text="Wann wurde die letzte Änderung vorgenommen?"
        "Wird automatisch gesetzt.",
        auto_now=True)

    def __unicode__(self):
        return self.kuerzel

    class Meta:
        verbose_name_plural = "Fachgebiete"
        verbose_name = "Fachgebiet"

##########################################


class Stellenart(models.Model):
    """Which types of Stellen exist?

    We assume that these do not change,
    but additional ones might appear in the future.
    """
    stellenart = models.CharField(
        "Stellenart",
        max_length=20,
        help_text="Welche Stellenarten unterscheiden wir?",
        primary_key=False,
        unique=True,
        )
    annmerkung = models.TextField("Anmerkungen",
                                  help_text="Beliebige Anmerkungen.",
                                  blank=True,
                                  )
    lastmodified = models.DateField(
        "Letzte Änderung",
        help_text="Wann wurde die letzte Änderung vorgenommen?"
        " Wird automatisch gesetzt.",
        auto_now=True)

    def __unicode__(self):
        return self.stellenart

    class Meta:
        verbose_name_plural = "Stellenarten"
        verbose_name = "Stellenart"

##########################################


class Stellenwertigkeit(models.Model):
    wertigkeit = models.CharField(
        "Wertigkeit",
        max_length=10,
        help_text="Welche Wertigkeiten für Stellen existieren?",
        primary_key=False,
        unique=True,
        )
    annmerkung = models.TextField("Anmerkungen",
                                  help_text="Beliebige Anmerkungen.",
                                  blank=True,
                                  )
    lastmodified = models.DateField(
        "Letzte Änderung",
        help_text="Wann wurde die letzte Änderung vorgenommen? "
        "Wird automatisch gesetzt.",
        auto_now=True)

    def __unicode__(self):
        return self.wertigkeit

    class Meta:
        verbose_name_plural = "Stellenwertigkeiten"
        verbose_name = "Stellenwertigkeit"

#######################


class StellenwertigkeitIntervalle(models.Model):
    """
    Stellenwertigkeiten können im Lauf der Zeit unterschiedliche
    Personalpunkte haben.
    """

    wertigkeit = models.ForeignKey(
        'Stellenwertigkeit',
        help_text='Intervalle für welche Wertigkeit?')

    personalpunkte = models.DecimalField(
        "Personalpunkte",
        max_digits=5,
        decimal_places=2,
        help_text="Wieviele Personalpunkte entsprechen "
        "einer solchen Wertigkeit?",
        )
    von = models.DateField(
        "Beginn Wertigkeit",
        help_text="Ab wann hat diese Wertigkeit diese Anzahl Personalpunkte?")
    bis = models.DateField(
        "Ende Wertigkeit",
        help_text="Bis wann hat diese Wertigkeit diese Anzahl Personalpunkte?")

    annmerkung = models.TextField(
        "Anmerkungen",
        help_text="Beliebige Anmerkungen.",
        blank=True,
        )
    lastmodified = models.DateField(
        "Letzte Änderung",
        help_text="Wann wurde die letzte Änderung vorgenommen? "
        "Wird automatisch gesetzt.",
        auto_now=True)

    def __unicode__(self):
        return ('Wertigkeit: {0:s} @ {1:s} Punkte ({2:s} - {3:s})'
                .format(self.wertigkeit,
                        str(self.personalpunkte),
                        str(self.von),
                        str(self.bis)))

    class Meta:
        verbose_name_plural = "Stellenwertigkeitsintervalle"
        verbose_name_plural = "Stellenwertigkeitsintervall"

##########################################


class Stelle(models.Model):
    stellennummer = models.DecimalField("Stellennummer",
                                        help_text="Eindeutige Stellennummer",
                                        unique=False,
                                        primary_key=False,
                                        max_digits=5,
                                        decimal_places=0,
    )
    wertigkeit = models.ForeignKey('Stellenwertigkeit',
                                   help_text="Wertigkeit der Stelle?")
    art = models.ForeignKey(
        'Stellenart',
        help_text="Welcher Art ist diese Stelle? (Land, ...)")

    von = models.DateField("Stellenbeginn",
                           help_text="Ab wann ist die Stelle verfügbar?")
    bis = models.DateField(
        "Stellenende",
        help_text="Wann endet die Verfügbarkeit der Stelle?")
    prozent = models.DecimalField(
        "Prozent",
        max_digits=3,
        decimal_places=0,
        help_text="Wieviel Prozent der VOLLEN Stelle?",
        )
    lehrkapazitaet = models.DecimalField(
        "Lehrkapazität",
        max_digits=5,
        decimal_places=2,
        help_text="Die mit dieser Stelle einhergehende Lehrkapazität, "
        "in SWS pro Semester",
        blank=True,
        )

    annmerkung = models.TextField("Anmerkungen",
                                  help_text="Beliebige Anmerkungen.",
                                  blank=True,
    )
    lastmodified = models.DateField(
        "Letzte Änderung",
        help_text="Wann wurde die letzte Änderung vorgenommen? "
        "Wird automatisch gesetzt.",
        auto_now=True)

    def __unicode__(self):
        return (unicode(self.stellennummer) +
                " (" + self.wertigkeit.wertigkeit +
                ", " + self.art.stellenart + ", " +
                monatsinterval(self) + ")"
                )

    class Meta:
        verbose_name_plural = "Stellen"
        verbose_name_plural = "Stelle"

##########################################


class Person(models.Model):
    """A real person

    No idea how to deal with name changes, e.g., divorce. Let's hope
    personnumber stays constant.
    """

    personalnummer = models.DecimalField("Personalnummer",
                                         help_text="Personalnummer der Person",
                                         primary_key=False,
                                         unique=False,
                                         max_digits=10,
                                         decimal_places=0, )
    name = models.CharField("Nachname",
                            help_text="Nachname",
                            max_length=50,
                            )
    vorname = models.CharField("Vorname",
                               help_text="Vorname",
                               max_length=50,
                               )

    annmerkung = models.TextField("Anmerkungen",
                                  help_text="Beliebige Anmerkungen.",
                                  blank=True,
                                  )
    lastmodified = models.DateField(
        "Letzte Änderung",
        help_text="Wann wurde die letzte Änderung vorgenommen? "
        "Wird automatisch gesetzt.",
        auto_now=True)

    def __unicode__(self):
        return (self.name + ", " +
                self.vorname + " (" +
                unicode(self.personalnummer) + ")")

    class Meta:
        verbose_name_plural = "Personen"
        verbose_name_plural = "Person"


class PersonZusage(models.Model):
    """Zusage an eine Person

    Einer PERSON koennen im Laufe der Zeit unterschiedliche Arten von
    STellen zugesagt werden.  Diese Zusage heißt nicht automatisch,
    dass dies auch erfüllt wird. Diese Klasse hält diese Zusagen an
    eine einzelne Person (nicht an eine Arbeitsgruppe fest).  Diese
    PersonZusage ist mit Besetzung zu vergleichen.
    """

    person = models.ForeignKey('Person',
                               help_text="Wem wurde diese Zusage gemacht?",
                               # to_field="Person"
                               )

    wertigkeit = models.ForeignKey('Stellenwertigkeit',
                                   help_text="Welche Wertigkeit hat "
                                   "der Vertrag?",
                                   to_field="wertigkeit")
    von = models.DateField("Einstellung",
                           help_text="Wann wurde die Person (auf "
                           "dieser Wertigkeit) eingestellt?")
    bis = models.DateField("Ende",
                           help_text="Wann endet das Arbeitsverhältnis "
                           "bzw. diese Wertigkeit?")
    prozent = models.DecimalField(
        "Prozent",
        max_digits=3,
        decimal_places=0,
        help_text="Wieviel Prozent der VOLLEN Arbeitszeit?",
        )
    lehrverpflichtung = models.DecimalField(
        "Lehrverpflichtung",
        max_digits=5,
        decimal_places=2,
        help_text="Persönliche Lehrverpflichtung in SWS pro Semester",
        blank=True,
        )
    annmerkung = models.TextField("Anmerkungen",
                                  help_text="Beliebige Anmerkungen.",
                                  blank=True,
    )
    lastmodified = models.DateField(
        "Letzte Änderung",
        help_text="Wann wurde die letzte Änderung vorgenommen? "
        "Wird automatisch gesetzt.",
        auto_now=True)

    class Meta:
        verbose_name_plural = "Zusagen an Personen"
        verbose_name_plural = "Zusage an Person"


##########################################


class Zusage(models.Model):
    """A promise about a stelle made to a Fachgebiet.

    Percentage of the full stelle, but that has to be decided
    how to deal with that elegantly. Beware of double
    multiplication.
    """

    fachgebiet = models.ForeignKey(
        'Fachgebiet',
        help_text="Welchem Fachgebiet wird die Zusage gemacht?")
    wertigkeit = models.ForeignKey(
        'Stellenwertigkeit',
        help_text="Welche Wertigkeit hat die zugesagte Stelle?")
    prozent = models.DecimalField(
        "Prozent",
        max_digits=3,
        decimal_places=0,
        help_text="Wieviel Prozent der VOLLEN Stellenwertigkeit "
        "werden zugesagt?",
    )
    von = models.DateField(
        "Zusagenbeginn",
        help_text="Ab wann gilt die Zusage?")
    bis = models.DateField(
        "Zusagenende",
        help_text="Bis wann gilt die Zusage?")
    annmerkung = models.TextField(
        "Anmerkungen",
        help_text="Beliebige Anmerkungen.",
        blank=True,
    )
    lastmodified = models.DateField(
        "Letzte Änderung",
        help_text="Wann wurde die letzte Änderung vorgenommen? "
        "Wird automatisch gesetzt.",
        auto_now=True)

    def __unicode__(self):
        return (self.wertigkeit.wertigkeit +
                "@" + self.fachgebiet.kuerzel +
                " (" + unicode(self.prozent) +
                ", " + monatsinterval(self) + ")")

    class Meta:
        verbose_name_plural = "Zusagen an Fachgebiete"
        verbose_name_plural = "Zusage an Fachgebiet"

##########################################


class Zuordnung(models.Model):
    fachgebiet = models.ForeignKey(
        'Fachgebiet',
        help_text="Welchem Fachgebiet wird die Stelle zugeordnet?")
    stelle = models.ForeignKey(
        'Stelle',
        help_text="Welche Stelle wird zugeordnet?")
    prozent = models.DecimalField(
        "Prozent",
        max_digits=3,
        decimal_places=0,
        help_text="Wieviel Prozent der VOLLEN Stellenwertigkeit "
        "werden zugeordnet?",
    )
    von = models.DateField(
        "Zuordnungsbeginn",
        help_text="Ab wann ist die Stelle dem Fachgebiet zugeordnet?")
    bis = models.DateField(
        "Zuordnungsende",
        help_text="Bis wann gilt die Zuordnung?")
    annmerkung = models.TextField(
        "Anmerkungen",
        help_text="Beliebige Anmerkungen.",
        blank=True,
    )
    lastmodified = models.DateField(
        "Letzte Änderung",
        help_text="Wann wurde die letzte Änderung vorgenommen? "
        "Wird automatisch gesetzt.",
        auto_now=True)

    def __unicode__(self):
        return (unicode(self.stelle.stellennummer) +
                "@" + self.fachgebiet.kuerzel + " (" +
                unicode(self.prozent) + ", " +
                monatsinterval(self) + ")")

    class Meta:
        verbose_name_plural = "Zuordnungen"
        verbose_name = "Zuordnung"

##########################################


class Besetzung(models.Model):
    person = models.ForeignKey(
        'Person',
        help_text="Welche Person wird auf eine Stelle besetzt?")
    stelle = models.ForeignKey(
        'Stelle',
        help_text="Welche Stelle wird besetzt?")
    prozent = models.DecimalField(
        "Prozent",
        max_digits=3,
        decimal_places=0,
        help_text="Wieviel Prozent der VOLLEN Stellenwertigkeit "
        "werden zugeordnet?",
    )
    von = models.DateField(
        "Besetzungsbeginn",
        help_text="Ab wann ist die Stelle mit der Person besetzt?")
    bis = models.DateField(
        "Besetzungsende",
        help_text="Bis wann ist die Stelle besetzt?")
    pseudo = models.BooleanField(
        "Pseudobesetzung?",
        help_text="Falls diese Stelle nur scheinbar mit NN besetzt wird, "
        "dieses Feld anklicken.",
        default=False,
    )
    annmerkung = models.TextField(
        "Anmerkungen",
        help_text="Beliebige Anmerkungen.",
        blank=True,
    )
    lastmodified = models.DateField(
        "Letzte Änderung",
        help_text="Wann wurde die letzte Änderung vorgenommen? "
        "Wird automatisch gesetzt.",
        auto_now=True)

    def __unicode__(self):
        return self.person.name + "@" + unicode(self.stelle.stellennummer)

    class Meta:
        verbose_name_plural = "Besetzungen"
        verbose_name = "Besetzung"
