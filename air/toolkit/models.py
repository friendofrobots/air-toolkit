from django.db import models
import toolkit.models

class Data(models.Model):
    profile = models.ForeignKey(FBGraph)
    graph = models.TextField()
    pmimatrix = models.TextField(blank=True)

    def __unicode__(self):
        return profile.
