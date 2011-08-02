from django.contrib.auth.models import User
from django.db import models
from django.db.models import Count
from django.db import transaction
from fbauth.models import FBLogin
from taggit.managers import TaggableManager
from picklefield.fields import PickledObjectField
from itertools import groupby
import json, pickle, math

class Profile(models.Model):
    user = models.OneToOneField(User,related_name='profile')
    fblogin = models.OneToOneField(FBLogin,related_name='profile')
    studying = models.BooleanField(default=False)
    stage = models.IntegerField(choices=(
            (0,'not yet started'),
            (1,'downloading user data'),
            (2,'calculating pmis'),
            (3,'done')
            ), default=0)
    last_updated = models.DateTimeField(auto_now=True)
    task_id = models.CharField(max_length=200,blank=True)
    minpmi = models.FloatField(blank=True,null=True)
    maxpmi = models.FloatField(blank=True,null=True)
    
    def getActivePages(self):
        return self.page_set.annotate(activity=Count('likedBy')).filter(activity__gt=1)

    def getActivePeople(self):
        return self.person_set.filter(likes__in=self.getActivePages()).distinct()

    def __unicode__(self):
        return self.fblogin.name

class Page(models.Model):
    owner = models.ForeignKey(Profile)
    fbid = models.CharField(max_length=50)
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=200)

    class Meta:
        unique_together = (('owner','fbid'))
        
    def topCategory(self):
        try:
            topscore = self.categoryScore.order_by('-value')[0]
            category_id = topscore.category_id
        except:
            category_id = None
        return category_id

    def __unicode__(self):
        return self.name

class PersonProperty(models.Model):
    RELATIONS = (
        ('gender','Gender'),
        ('hometown','Hometown'),
        ('location','Location'),
        ('school','School'),
        ('work','Work'),
        ('relationship','Relationship Status')
        )
    owner = models.ForeignKey(Profile)
    relation = models.CharField(max_length=50, choices=RELATIONS)
    name = models.CharField(max_length=200)

    class Meta:
        unique_together = (('owner','relation','name'))

    def __unicode__(self):
        return self.relation +' - '+ self.name

class Person(models.Model):
    owner = models.ForeignKey(Profile)
    fbid = models.CharField(max_length=50)
    name = models.CharField(max_length=200)
    likes = models.ManyToManyField(Page,blank=True,related_name='likedBy')
    properties = models.ManyToManyField(PersonProperty,blank=True,related_name="people")

    class Meta:
        unique_together = (('owner','fbid'))

    def __unicode__(self):
        return self.name

class PMI(models.Model):
    owner = models.ForeignKey(Profile)
    fromPage = models.ForeignKey(Page,related_name='pmisFrom')
    toPage = models.ForeignKey(Page,related_name='pmisTo')
    value = models.FloatField()

    class Meta:
        unique_together = (('owner','fromPage','toPage'))
    
    def npmi(self):
        numpeople = self.owner.getActivePeople().count()
        npmi = -1. * self.value / math.log(1.*max(self.fromPage.likedBy.count(),
                                                  self.toPage.likedBy.count())/numpeople,2)
        return (1 + npmi)/2

    def normalized_value(self):
        return (self.value - self.owner.minpmi) / (self.owner.maxpmi - self.owner.minpmi)

    def __unicode__(self):
        return self.fromPage.name +","+ self.toPage.name +"=>"+ unicode(self.value)
    
class Category(models.Model):
    owner = models.ForeignKey(Profile,related_name="categories")
    name = models.CharField(max_length=200)
    seeds = models.ManyToManyField(Page,blank=True,related_name="seedOf")
    active = models.OneToOneField(Profile,related_name="activeCategory",blank=True,null=True)
    task_id = models.CharField(max_length=200,blank=True)
    status = PickledObjectField(blank=True,default={'rounds':[],'processing':False,'error':''})

    ready = models.BooleanField(default=False)
    unread = models.BooleanField(default=False)
    last_updated = models.DateTimeField(auto_now=True)

    startvalue = models.FloatField(default=0.6)
    threshold = models.FloatField(default=0.4)
    decayrate = models.FloatField(default=0.3)

    tags = TaggableManager(blank=True)

    def getTopPage(self):
        return self.scores.order_by('-value','page__fbid')[0].page

    def getTop(self,num=12):
        return self.scores.order_by('-value','page__fbid')[:num]

    def getTopPeople(self,num=4):
        return self.memberships.order_by('-value','member__fbid')[:num]

    def reset(self):
        self.unread = False
        self.ready = False
        self.task_id = ""
        self.status = {'rounds':[],'processing':False,'error':''}
        self.save()

    def clearStatus(self,processing=False):
        self.status = {'rounds':[],'processing':processing,'error':''}
        self.save()

    def newRoundStatus(self,num):
        status = self.status
        status['rounds'].append(num)
        self.status = status
        self.save()

    def updateRoundStatus(self,num):
        status = self.status
        status['rounds'][-1] = num
        self.status = status
        self.save()

    def getStatus(self):
        if self.status:
            status = pickle.loads(str(self.status))
        else:
            status = []
        return status

    def resetScores(self, auto=True):
        if not self.scores.exists():
            pages = self.owner.getActivePages()
            for page in pages:
                CategoryScore.objects.get_or_create(owner=self.owner,
                                                    category=self,
                                                    page=page)
        with transaction.commit_on_success():
            self.scores.all().update(value=0,fired=False)
            try:
                scores = self.scores.filter(page__likedBy__in=self.group.people.all()).distinct()
                act = scores.annotate(activity=Count('page__likedBy'))
                max_act = max(act,key=lambda x : x.activity).activity
                mult = self.startvalue/(1.*max_act)
                for act_value,iterscores in groupby(sorted(act,key=lambda a : a.activity),lambda x : x.activity):
                    self.scores.filter(id__in=act.filter(activity=act_value)).update(value=act_value*mult)
                if auto:
                    self.threshold = max(min(self.scores.order_by('-value')[2].value - .01,.2),.15)
                    self.decayrate = min(.18, self.startvalue * max_act/10)
                    
                    self.save()
            except PersonGroup.DoesNotExist:
                self.scores.filter(page__in=self.seeds.all()).update(value=self.startvalue)

    def calcMemberships(self):
        with transaction.commit_on_success():
            if not self.memberships.exists():
                people = self.owner.getActivePeople()
                for person in people:
                    CategoryMembership.objects.get_or_create(owner=self.owner,
                                                             category=self,
                                                             member=person)
        self.memberships.update(value=0)
        with transaction.commit_on_success():
            for membership in self.memberships.all():
                value = 0
                for score in self.scores.filter(page__in=membership.member.likes.all()):
                    value += score.value
                membership.value = value
                membership.save()

    def __unicode__(self):
        return self.name

class CategoryScore(models.Model):
    owner = models.ForeignKey(Profile)
    category = models.ForeignKey(Category,related_name="scores")
    page = models.ForeignKey(Page,related_name="categoryScore")
    value = models.FloatField(default=0.0)
    fired = models.BooleanField(default=False)

    def normalized_value(self):
        return self.value

    def __unicode__(self):
        return self.category.name + ': ' + self.page.name + ' - ' + unicode(self.value)

class CategoryMembership(models.Model):
    owner = models.ForeignKey(Profile)
    category = models.ForeignKey(Category,related_name="memberships")
    member = models.ForeignKey(Person,related_name="categoryMembership")
    value = models.FloatField(default=0.0)

    def __unicode__(self):
        return self.category.name + ': ' + self.member.name + ' - ' + unicode(self.value)

class PersonGroup(models.Model):
    owner = models.ForeignKey(Profile)
    category = models.OneToOneField(Category,related_name="group")
    people = models.ManyToManyField(Person,related_name="group")

    def __unicode__(self):
        return self.category.name + ' Group'
