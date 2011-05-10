from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User,related_name='profile')
    fbid = models.CharField(unique=True,max_length=30)
    name = models.CharField(max_length=200)
    access_token = models.CharField(max_length=200,blank=True)
    def __unicode__(self):
        return self.name
