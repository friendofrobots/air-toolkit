from django.db import models
from django.db.models import Count
from django.db import transaction
from fbauth.models import Profile
from taggit.managers import TaggableManager
import json, pickle, math

class DownloadStatus(models.Model):
    owner = models.OneToOneField(Profile,related_name="status")
    stage = models.IntegerField(choices=(
            (0,'not yet started'),
            (1,'downloading user data'),
            (2,'calculating pmis'),
            (3,'done')
            ), default=0)
    last_updated = models.DateTimeField(auto_now=True)
    task_id = models.CharField(max_length=200,blank=True)
    numpeople = models.IntegerField(blank=True,null=True) # filtered for people with likes
    minpmi = models.FloatField(blank=True,null=True)
    maxpmi = models.FloatField(blank=True,null=True)

    def __unicode__(self):
        return self.owner.name + "'s Status"

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
        numpeople = self.owner.status.numpeople
        npmi = -1. * self.value / math.log(1.*max(self.fromPage.likedBy.count(),
                                                  self.toPage.likedBy.count())/numpeople,2)
        return (1 + npmi)/2

    def normalized_value(self):
        status = self.owner.status
        return (self.value - status.minpmi) / (status.maxpmi - status.minpmi)

    def __unicode__(self):
        return self.fromPage.name +","+ self.toPage.name +"=>"+ unicode(self.value)
    
class Category(models.Model):
    owner = models.ForeignKey(Profile,related_name="categories")
    name = models.CharField(max_length=200)
    seeds = models.ManyToManyField(Page,blank=True,related_name="seedOf")
    active = models.OneToOneField(Profile,related_name="activeCategory",blank=True,null=True)
    task_id = models.CharField(max_length=200,blank=True)
    status = models.TextField(blank=True)

    ready = models.BooleanField(default=False)
    unread = models.BooleanField(default=False)
    last_updated = models.DateField(auto_now=True)

    startvalue = models.FloatField(default=0.6)
    threshold = models.FloatField(default=0.4)
    decayrate = models.FloatField(default=0.3)

    tags = TaggableManager()

    def getASeed(self):
        return self.seeds.all()[0]

    def getTop(self,num=12):
        return self.scores.order_by('-value','page__fbid')[:num]

    def getTopPeople(self,num=4):
        return self.memberships.order_by('-value','member__fbid')[:num]

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

    def resetScores(self):
        if not category.scores.exists():
            pages = Page.objects.filter(owner=profile).annotate(activity=Count('likedBy')).filter(activity__gt=1)
            for page in pages:
                CategoryScore.objects.get_or_create(owner=profile,
                                                    category=category,
                                                    page=page)
        self.scores.all().update(value=0)
        try:
            self.scores.filter(page__likedBy__in=self.group.people.all())
            seedCount = {}
            for person in self.group.people.all():
                for like in person.likes.all():
                    if like not in seedCount:
                        seedCount[like] = 0
                    seedCount[like] += 1
        mult = self.startvalue/(1.*max(seedCount.iteritems(),key=lambda x : x[1]))
        except PersonGroup.DoesNotExist:
            self.scores.filter(page__in=self.seeds.all()).update(value=self.startvalue)

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

    def getPage(self):
        return self.page

    def resetScores(self):
        if not self.scores.exists():
            pages = Page.objects.filter(owner=self.owner).annotate(activity=Count('likedBy')).filter(activity__gt=1)
            for page in pages:
                CategoryScore.objects.get_or_create(owner=self.owner,
                                                    category=self,
                                                    page=page)
        self.scores.update(value=0.0,fired=False)
        try:
            self.collection.seedCategory()
        except:
            self.scores.filter(page__in=self.seeds.all()).update(value=self.startvalue)

    def calcMemberships(self):
        with transaction.commit_on_success():
            for person in Person.objects.filter(owner=self.owner):
                membership = 0
                for score in self.scores.filter(page__in=person.likes.all()):
                    membership += score.value
                    CategoryMembership.objects.get_or_create(
                        owner=self.owner,
                        category=self,
                        member=person,
                        value=membership)

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

    def seedCategory(self):
        pass

    def __unicode__(self):
        return self.category.name + ' Group'
