from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.ForeignKey(User)
    access_token = models.CharField(max_length=200)
    friends = models.TextField(blank=True)
    profile_data = models.TextField(blank=True)
    graph_pickle = models.TextField(blank=True)
    graph_file = models.TextField(blank=True)
    
