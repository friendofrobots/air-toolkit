from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.ForeignKey(User)
    fbid = models.CharField(max_length=30)
    name = models.CharField(max_length=200)
    access_token = models.CharField(max_length=200)
    
