# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Besetzung',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('prozent', models.DecimalField(help_text=b'Wieviel Prozent der VOLLEN Stellenwertigkeit werden zugeordnet?', verbose_name=b'Prozent', max_digits=3, decimal_places=0)),
                ('von', models.DateField(help_text=b'Ab wann ist die Stelle mit der Person besetzt?', verbose_name=b'Besetzungsbeginn')),
                ('bis', models.DateField(help_text=b'Bis wann ist die Stelle besetzt?', verbose_name=b'Besetzungsende')),
                ('pseudo', models.BooleanField(default=False, help_text=b'Falls diese Stelle nur scheinbar mit NN besetzt wird, dieses Feld anklicken.', verbose_name=b'Pseudobesetzung?')),
                ('annmerkung', models.TextField(help_text=b'Beliebige Anmerkungen.', verbose_name=b'Anmerkungen', blank=True)),
                ('lastmodified', models.DateField(help_text=b'Wann wurde die letzte \xc3\x84nderung vorgenommen? Wird automatisch gesetzt.', verbose_name=b'Letzte \xc3\x84nderung', auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Fachgebiet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('kuerzel', models.CharField(help_text=b'Ein K\xc3\xbcrzel f\xc3\xbcr das Fachgebiet, meist einige Buchstaben.', max_length=10, verbose_name=b'Fachgebietsk\xc3\xbcrzel')),
                ('fgname', models.CharField(help_text=b'Der offizielle Name des Fachgebietes', max_length=50, verbose_name=b'Fachgebietsname')),
                ('von', models.DateField(help_text=b'Wann wurde das Fachgebiet eingerichtet?', verbose_name=b'Einrichtungsdatum')),
                ('bis', models.DateField(help_text=b'Wann wird das Fachgebiet aufgel\xc3\xb6st?', verbose_name=b'Aufl\xc3\xb6sungsdatum')),
                ('kostenstelle', models.DecimalField(help_text=b'Abrechnungsobjekt des Fachgebiets', verbose_name=b'Abrechnungsobjekt', max_digits=10, decimal_places=0, blank=True)),
                ('annmerkung', models.TextField(help_text=b'Beliebige Anmerkungen.', verbose_name=b'Anmerkungen', blank=True)),
                ('lastmodified', models.DateField(help_text=b'Wann wurde die letzte \xc3\x84nderung vorgenommen? Wird automatisch gesetzt.', verbose_name=b'Letzte \xc3\x84nderung', auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('personalnummer', models.DecimalField(help_text=b'Personalnummer der Person', verbose_name=b'Personalnummer', max_digits=10, decimal_places=0)),
                ('name', models.CharField(help_text=b'Nachname', max_length=50, verbose_name=b'Nachname')),
                ('vorname', models.CharField(help_text=b'Vorname', max_length=50, verbose_name=b'Vorname')),
                ('annmerkung', models.TextField(help_text=b'Beliebige Anmerkungen.', verbose_name=b'Anmerkungen', blank=True)),
                ('lastmodified', models.DateField(help_text=b'Wann wurde die letzte \xc3\x84nderung vorgenommen? Wird automatisch gesetzt.', verbose_name=b'Letzte \xc3\x84nderung', auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PersonZusage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('von', models.DateField(help_text=b'Wann wurde die Person (auf dieser Wertigkeit) eingestellt?', verbose_name=b'Einstellung')),
                ('bis', models.DateField(help_text=b'Wann endet das Arbeitsverh\xc3\xa4ltnis bzw. diese Wertigkeit?', verbose_name=b'Ende')),
                ('prozent', models.DecimalField(help_text=b'Wieviel Prozent der VOLLEN Arbeitszeit?', verbose_name=b'Prozent', max_digits=3, decimal_places=0)),
                ('lehrverpflichtung', models.DecimalField(help_text=b'Pers\xc3\xb6nliche Lehrverpflichtung in SWS pro Semester', verbose_name=b'Lehrverpflichtung', max_digits=5, decimal_places=2, blank=True)),
                ('annmerkung', models.TextField(help_text=b'Beliebige Anmerkungen.', verbose_name=b'Anmerkungen', blank=True)),
                ('lastmodified', models.DateField(help_text=b'Wann wurde die letzte \xc3\x84nderung vorgenommen? Wird automatisch gesetzt.', verbose_name=b'Letzte \xc3\x84nderung', auto_now=True)),
                ('person', models.ForeignKey(help_text=b'Wem wurde diese Zusage gemacht?', to='stellenplan.Person')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Stelle',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('stellennummer', models.DecimalField(help_text=b'Eindeutige Stellennummer', verbose_name=b'Stellennummer', max_digits=5, decimal_places=0)),
                ('von', models.DateField(help_text=b'Ab wann ist die Stelle verf\xc3\xbcgbar?', verbose_name=b'Stellenbeginn')),
                ('bis', models.DateField(help_text=b'Wann endet die Verf\xc3\xbcgbarkeit der Stelle?', verbose_name=b'Stellenende')),
                ('prozent', models.DecimalField(help_text=b'Wieviel Prozent der VOLLEN Stelle?', verbose_name=b'Prozent', max_digits=3, decimal_places=0)),
                ('lehrkapazitaet', models.DecimalField(help_text=b'Die mit dieser Stelle einhergehende Lehrkapazit\xc3\xa4t, in SWS pro Semester', verbose_name=b'Lehrkapazit\xc3\xa4t', max_digits=5, decimal_places=2, blank=True)),
                ('annmerkung', models.TextField(help_text=b'Beliebige Anmerkungen.', verbose_name=b'Anmerkungen', blank=True)),
                ('lastmodified', models.DateField(help_text=b'Wann wurde die letzte \xc3\x84nderung vorgenommen? Wird automatisch gesetzt.', verbose_name=b'Letzte \xc3\x84nderung', auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Stellenart',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('stellenart', models.CharField(help_text=b'Welche Stellenarten unterscheiden wir?', unique=True, max_length=20, verbose_name=b'Stellenart')),
                ('annmerkung', models.TextField(help_text=b'Beliebige Anmerkungen.', verbose_name=b'Anmerkungen', blank=True)),
                ('lastmodified', models.DateField(help_text=b'Wann wurde die letzte \xc3\x84nderung vorgenommen? Wird automatisch gesetzt.', verbose_name=b'Letzte \xc3\x84nderung', auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Stellenwertigkeit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('wertigkeit', models.CharField(help_text=b'Welche Wertigkeiten f\xc3\xbcr Stellen existieren?', unique=True, max_length=10, verbose_name=b'Wertigkeit')),
                ('annmerkung', models.TextField(help_text=b'Beliebige Anmerkungen.', verbose_name=b'Anmerkungen', blank=True)),
                ('lastmodified', models.DateField(help_text=b'Wann wurde die letzte \xc3\x84nderung vorgenommen? Wird automatisch gesetzt.', verbose_name=b'Letzte \xc3\x84nderung', auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StellenwertigkeitIntervalle',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('personalpunkte', models.DecimalField(help_text=b'Wieviele Personalpunkte entsprechen einer solchen Wertigkeit?', verbose_name=b'Personalpunkte', max_digits=5, decimal_places=2)),
                ('von', models.DateField(help_text=b'Ab wann hat diese Wertigkeit diese Anzahl Personalpunkte?', verbose_name=b'Beginn Wertigkeit')),
                ('bis', models.DateField(help_text=b'Bis wann hat diese Wertigkeit diese Anzahl Personalpunkte?', verbose_name=b'Ende Wertigkeit')),
                ('annmerkung', models.TextField(help_text=b'Beliebige Anmerkungen.', verbose_name=b'Anmerkungen', blank=True)),
                ('lastmodified', models.DateField(help_text=b'Wann wurde die letzte \xc3\x84nderung vorgenommen? Wird automatisch gesetzt.', verbose_name=b'Letzte \xc3\x84nderung', auto_now=True)),
                ('wertigkeit', models.ForeignKey(help_text=b'Intervalle f\xc3\xbcr welche Wertigkeit?', to='stellenplan.Stellenwertigkeit')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Zuordnung',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('prozent', models.DecimalField(help_text=b'Wieviel Prozent der VOLLEN Stellenwertigkeit werden zugeordnet?', verbose_name=b'Prozent', max_digits=3, decimal_places=0)),
                ('von', models.DateField(help_text=b'Ab wann ist die Stelle dem Fachgebiet zugeordnet?', verbose_name=b'Zuordnungsbeginn')),
                ('bis', models.DateField(help_text=b'Bis wann gilt die Zuordnung?', verbose_name=b'Zuordnungsende')),
                ('annmerkung', models.TextField(help_text=b'Beliebige Anmerkungen.', verbose_name=b'Anmerkungen', blank=True)),
                ('lastmodified', models.DateField(help_text=b'Wann wurde die letzte \xc3\x84nderung vorgenommen? Wird automatisch gesetzt.', verbose_name=b'Letzte \xc3\x84nderung', auto_now=True)),
                ('fachgebiet', models.ForeignKey(help_text=b'Welchem Fachgebiet wird die Stelle zugeordnet?', to='stellenplan.Fachgebiet')),
                ('stelle', models.ForeignKey(help_text=b'Welche Stelle wird zugeordnet?', to='stellenplan.Stelle')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Zusage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('prozent', models.DecimalField(help_text=b'Wieviel Prozent der VOLLEN Stellenwertigkeit werden zugesagt?', verbose_name=b'Prozent', max_digits=3, decimal_places=0)),
                ('von', models.DateField(help_text=b'Ab wann gilt die Zusage?', verbose_name=b'Zusagenbeginn')),
                ('bis', models.DateField(help_text=b'Bis wann gilt die Zusage?', verbose_name=b'Zusagenende')),
                ('annmerkung', models.TextField(help_text=b'Beliebige Anmerkungen.', verbose_name=b'Anmerkungen', blank=True)),
                ('lastmodified', models.DateField(help_text=b'Wann wurde die letzte \xc3\x84nderung vorgenommen? Wird automatisch gesetzt.', verbose_name=b'Letzte \xc3\x84nderung', auto_now=True)),
                ('fachgebiet', models.ForeignKey(help_text=b'Welchem Fachgebiet wird die Zusage gemacht?', to='stellenplan.Fachgebiet')),
                ('wertigkeit', models.ForeignKey(help_text=b'Welche Wertigkeit hat die zugesagte Stelle?', to='stellenplan.Stellenwertigkeit')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='stelle',
            name='art',
            field=models.ForeignKey(help_text=b'Welcher Art ist diese Stelle? (Land, ...)', to='stellenplan.Stellenart'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='stelle',
            name='wertigkeit',
            field=models.ForeignKey(help_text=b'Wertigkeit der Stelle?', to='stellenplan.Stellenwertigkeit'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='personzusage',
            name='wertigkeit',
            field=models.ForeignKey(to='stellenplan.Stellenwertigkeit', help_text=b'Welche Wertigkeit hat der Vertrag?', to_field=b'wertigkeit'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='besetzung',
            name='person',
            field=models.ForeignKey(help_text=b'Welche Person wird auf eine Stelle besetzt?', to='stellenplan.Person'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='besetzung',
            name='stelle',
            field=models.ForeignKey(help_text=b'Welche Stelle wird besetzt?', to='stellenplan.Stelle'),
            preserve_default=True,
        ),
    ]
