from django.db import models

# Create your models here.
class FBGraph(models.Model):
    filename = models.CharField(max_length=100)
    altered = models.BooleanField()

    def __unicode__(self):
        return self.filename
