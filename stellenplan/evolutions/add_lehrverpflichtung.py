from django_evolution.mutations import AddField
from django.db import models


MUTATIONS = [
    AddField('Person', 'lehrverpflichtung', models.DecimalField, initial=0, max_digits=5, decimal_places=2)
]

