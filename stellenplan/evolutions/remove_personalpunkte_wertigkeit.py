__author__ = 'hkarl'

from django_evolution.mutations import DeleteField


MUTATIONS = [
    DeleteField('Stellenwertigkeit', 'personalpunkte')
]
