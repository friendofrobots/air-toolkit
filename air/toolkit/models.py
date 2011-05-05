from django.db import models
from fbauth.models import Profile

class DownloadStatus(models.Model):
    owner = models.ForeignKey(Profile,related_name="downloadStatus")
    stage = models.IntegerField(choices=(
            (0,'not yet started'),
            (1,'downloading user data'),
            (2,'calculating pmis'),
            (3,'done')
            ), default=0)
    lastupdated = models.DateTimeField(auto_now=True)
    task_id = models.CharField(max_length=200,blank=True)

class Entity(models.Model):
    owner = models.ForeignKey(Profile)
    fbid = models.CharField(max_length=50)
    name = models.CharField(max_length=200)

    def getpmis(self):
        return PMI.objects.filter(models.Q(toEntity=self) | models.Q(fromEntity=self)).distinct().order_by('-value')

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
    seeds = models.ManyToManyField(Entity)
    active = models.OneToOneField(Profile,related_name="activeCategory",blank=True,null=True)
    task_id = models.CharField(max_length=200,blank=True)

    def __unicode__(self):
        return self.name

class CategoryScore(models.Model):
    owner = models.ForeignKey(Profile)
    category = models.ForeignKey(Category,related_name="scores")
    entity = models.ForeignKey(Entity,related_name="categoryScore")
    value = models.FloatField(default=0.0)
    fired = models.BoolField(default=False)

    def __unicode__(self):
        return self.category.name + ': ' + self.entity.name + ' - ' + unicode(self.value)
