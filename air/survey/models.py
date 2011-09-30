from django.db import models
from toolkit.models import *

class Survey(models.Model):
    owner = models.ForeignKey(Profile,related_name="surveys")
    category = models.ForeignKey(Category,related_name="survey")

    # How well does this group of likes represent the likes of any individual person?
    individual = models.IntegerField(choices=(
            (1,'1: not at all'),
            (2,'2'),(3,'3'),(4,'4'),(5,'5'),(6,'6'),
            (7,'7: perfect match'),
            ), blank=True,null=True)

    # Please fill in the following blanks with descriptive titles of subgroups you
    # would make if you were to divide this set of likes.
    subgroup1 = models.CharField(blank=True,max_length=140)
    subgroup2 = models.CharField(blank=True,max_length=140)
    subgroup3 = models.CharField(blank=True,max_length=140)

    # If I showed you this collection of Likes without telling you how it was generated,
    # what would you see as the unifying factor? (It's okay if it's the same or different
    # than what we actually used)
    unifying = models.CharField(blank=True,max_length=200)

    # Are there any likes you are surprised about? Please choose up to 2 and describe
    # what about them you find surprising.
    surprise1_page = models.ForeignKey(Page,null=True,related_name="survey_surprise1")
    surprise1_describe = models.TextField(blank=True)
    surprise2_page = models.ForeignKey(Page,null=True,related_name="survey_surprise2")
    surprise2_describe = models.TextField(blank=True)

    # If you were hiring an actor to play someone in this group of people,
    # how useful would this list be in describing what sort of persona they should take?
    actor = models.IntegerField(choices=(
            (1,'1: not at all'),
            (2,'2'),(3,'3'),(4,'4'),(5,'5'),(6,'6'),
            (7,'7: extremely useful'),
            ), blank=True,null=True)

    # How much have you learned from this group of likes that you didn't know or didn't realize
    # about the people before?
    learned = models.IntegerField(choices=(
            (1,'1: absolutely nothing'),
            (2,'2'),(3,'3'),(4,'4'),(5,'5'),(6,'6'),
            (7,'7: I learned a lot'),
            ), blank=True,null=True)

    # Do you have any futher thoughts about the category?
    further_thoughts = models.TextField(blank=True)

    def __unicode__(self):
        return self.owner.fblogin.name+' - '+self.category.name+' survey'
