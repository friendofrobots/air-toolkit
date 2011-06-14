from django.db import models
from django.db.models import Count
from fbauth.models import Profile
import json,pickle

class DownloadStatus(models.Model):
    owner = models.OneToOneField(Profile,related_name="downloadStatus")
    stage = models.IntegerField(choices=(
            (0,'not yet started'),
            (1,'downloading user data'),
            (2,'calculating pmis'),
            (3,'finding categories'),
            (4,'done')
            ), default=0)
    lastupdated = models.DateTimeField(auto_now=True)
    task_id = models.CharField(max_length=200,blank=True)

class Entity(models.Model):
    owner = models.ForeignKey(Profile)
    fbid = models.CharField(max_length=50)
    name = models.CharField(max_length=200)

    # Like methods
    def likedBy(self):
        # Caution: returns a set instead of a QuerySet
        return set([link.fromEntity for link in self.linksTo.filter(relation="likes").select_related()])

    def getpmis(self):
        return PMI.objects.filter(models.Q(toEntity=self) | models.Q(fromEntity=self)).distinct().select_related().order_by('-value')

    def topCategory(self):
        try:
            topscore = self.categoryScore.order_by('-value')[0]
            category_id = topscore.category_id
        except:
            category_id = None
        return category_id

    # Profile methods
    def likes(self):
        # Caution: returns a set of links, not entities
        counted = self.linksFrom.filter(relation="likes").annotate(entity_activity=Count('toEntity__linksTo'))
        return counted.filter(entity_activity__gt=1).select_related()

    def __unicode__(self):
        return self.name

class Link(models.Model):
    owner = models.ForeignKey(Profile)
    relation = models.CharField(max_length=100)
    fromEntity = models.ForeignKey(Entity,related_name='linksFrom')
    toEntity = models.ForeignKey(Entity,related_name='linksTo')
    weight = models.FloatField(default=1.0)

    def __unicode__(self):
        return unicode((self.fromEntity.name,
                        self.relation,
                        self.weight,
                        self.toEntity.name))

class PMI(models.Model):
    owner = models.ForeignKey(Profile)
    fromEntity = models.ForeignKey(Entity,related_name='pmiFrom')
    toEntity = models.ForeignKey(Entity,related_name='pmiTo')
    value = models.FloatField()

    def __unicode__(self):
        return self.fromEntity.name +","+ self.toEntity.name +"=>"+ unicode(self.value)
    
class Category(models.Model):
    owner = models.ForeignKey(Profile)
    name = models.CharField(max_length=200)
    seeds = models.ManyToManyField(Entity,blank=True)
    active = models.OneToOneField(Profile,related_name="activeCategory",blank=True,null=True)
    task_id = models.CharField(max_length=200,blank=True)
    status = models.TextField(blank=True)
    startvalue = models.FloatField(default=0.6)
    threshold = models.FloatField(default=0.4)
    decayrate = models.FloatField(default=0.3)
    

    def getTop(self,num=12):
        return self.scores.order_by('-value')[:num]

    def getTopPeople(self,num=10):
        # I might actually want to calculate membership gradience for each
        # entity ahead of time
        return num

    def addNumToStatus(self,num):
        if not self.status:
            self.status = pickle.dumps([])
        newstatus = pickle.loads(str(self.status))
        newstatus.append(num)
        self.status = pickle.dumps(newstatus)
        self.save()

    def getStatus(self):
        if self.status:
            status = pickle.loads(str(self.status))
        else:
            status = []
        return status

    def __unicode__(self):
        return self.name

class CategoryScore(models.Model):
    owner = models.ForeignKey(Profile)
    category = models.ForeignKey(Category,related_name="scores")
    entity = models.ForeignKey(Entity,related_name="categoryScore")
    value = models.FloatField(default=0.0)
    fired = models.BooleanField(default=False)

    def __unicode__(self):
        return self.category.name + ': ' + self.entity.name + ' - ' + unicode(self.value)
