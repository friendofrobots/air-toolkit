from django.db import models
from fbauth.models import Profile
from toolkit.models import Person, Page, Category

class Survey(models.Model):
    owner = models.OneToOneField(Profile,related_name="downloadStatus")
    category = models.OneToOneField(Category,related_name="surveyResults")
    # How well does this category represent a group of your friends? (representative)
    representative = models.IntegerField(choices=(
            (1,''),
            (2,''),(3,''),(4,''),(5,''),(6,''),
            (7,''),
            ), blank=True)
    # Is this category a positive or negative representation of those friends? (kind of stereotype/ideal)
    representative = models.IntegerField(choices=(
            (1,''),
            (2,''),(3,''),(4,''),(5,''),(6,''),
            (7,''),
            ), blank=True)
    # Is there a single person that best represents this category? (paragon)
    representative = models.IntegerField(choices=(
            (1,''),
            (2,''),(3,''),(4,''),(5,''),(6,''),
            (7,''),
            ), blank=True)
    # How central are these objects to the category? (shown with the top 3)
    representative = models.IntegerField(choices=(
            (1,''),
            (2,''),(3,''),(4,''),(5,''),(6,''),
            (7,''),
            ), blank=True)

    # Are there any surprising items in the category?
    representative = models.IntegerField(choices=(
            (1,''),
            (2,''),(3,''),(4,''),(5,''),(6,''),
            (7,''),
            ), blank=True)
    # Are the people associated with the category surprising?
    representative = models.IntegerField(choices=(
            (1,''),
            (2,''),(3,''),(4,''),(5,''),(6,''),
            (7,''),
            ), blank=True)

    # Would the top people associated with this category make a useful Facebook List?
    representative = models.IntegerField(choices=(
            (1,''),
            (2,''),(3,''),(4,''),(5,''),(6,''),
            (7,''),
            ), blank=True)
    # Would you like to have these people grouped together for privacy reasons (either hiding things from them or hiding things they post from others)
    representative = models.IntegerField(choices=(
            (1,''),
            (2,''),(3,''),(4,''),(5,''),(6,''),
            (7,''),
            ), blank=True)
    # Would the people associated with this group make a useful Facebook Group.
    representative = models.IntegerField(choices=(
            (1,''),
            (2,''),(3,''),(4,''),(5,''),(6,''),
            (7,''),
            ), blank=True)

class SurveyForm(ModelForm):
    class Meta:
        model = Survey
