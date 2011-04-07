from django.db import models
from fbauth.models import Profile

class Data(models.Model):
    profile = models.ForeignKey(Profile)
    graph = models.TextField()
    pmimatrix = models.TextField(blank=True)

    def __unicode__(self):
        return profile.name
