from django.db import models
from fbauth.models import Profile
from toolkit.models import Person, Page, Category

class Survey(models.Model):
    owner = models.OneToOneField(Profile,related_name="survey")
    category = models.OneToOneField(Category,related_name="surveyResults")
    question_number = 
    # How well does this category represent a group of your friends? (representative)
    representative = models.IntegerField(choices=(
            (1,''),
            (2,''),(3,''),(4,''),(5,''),(6,''),
            (7,''),
            ), blank=True)
    # Is this category a positive or negative representation of those friends? (kind of stereotype/ideal)
    posneg = models.IntegerField(choices=(
            (1,''),
            (2,''),(3,''),(4,''),(5,''),(6,''),
            (7,''),
            ), blank=True)
    # Is there a single person that best represents this category? (paragon)
    paragon = models.IntegerField(choices=(
            (1,''),
            (2,''),(3,''),(4,''),(5,''),(6,''),
            (7,''),
            ), blank=True)
    # How central are these objects to the category? (shown with the top 3)
    centrality = models.IntegerField(choices=(
            (1,''),
            (2,''),(3,''),(4,''),(5,''),(6,''),
            (7,''),
            ), blank=True)

    # Are there any surprising items in the category?
    surprise_items = models.IntegerField(choices=(
            (1,''),
            (2,''),(3,''),(4,''),(5,''),(6,''),
            (7,''),
            ), blank=True)
    # Are the people associated with the category surprising?
    surprise_people = models.IntegerField(choices=(
            (1,''),
            (2,''),(3,''),(4,''),(5,''),(6,''),
            (7,''),
            ), blank=True)

    # Would the top people associated with this category make a useful Facebook List?
    useful_list = models.IntegerField(choices=(
            (1,''),
            (2,''),(3,''),(4,''),(5,''),(6,''),
            (7,''),
            ), blank=True)
    # Would you like to have these people grouped together for privacy reasons? (either hiding things from them or hiding things they post from others)
    useful_privacy = models.IntegerField(choices=(
            (1,''),
            (2,''),(3,''),(4,''),(5,''),(6,''),
            (7,''),
            ), blank=True)
    # Would the people associated with this group make a useful Facebook Group?
    useful_group = models.IntegerField(choices=(
            (1,''),
            (2,''),(3,''),(4,''),(5,''),(6,''),
            (7,''),
            ), blank=True)

    def set_question(self, q_num, value):
        if q_num == 1:
            self.representative = value
        elif q_num == 2:
            self.posneg = value
        elif q_num == 3:
            self.paragon = value
        elif q_num == 4:
            self.centrality = value
        elif q_num == 5:
            self.surprise_items = value
        elif q_num == 6:
            self.surprize_people = value
        elif q_num == 7:
            self.useful_list = value
        elif q_num == 8:
            self.useful_privacy = value
        elif q_num == 9:
            self.useful_group = value
        else:
            'error'
