from django.db import models
from fbauth.models import Profile

class Data(models.Model):
    profile = models.ForeignKey(Profile)
    graph = models.TextField()
    lookup = models.TextField()
    filtered_graph = models.TextField(blank=True)
    pmi_matrix = models.TextField(blank=True)

    def __unicode__(self):
        return self.profile.name
