from django.db import models
from fbauth.models import Profile

class Entity(models.Model):
    fbid = models.CharField(max_length=30)
    name = models.CharField(max_length=200)

    def __unicode__(self):
        return self.name

class Link(models.Model):
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
    fromEntity = models.ForeignKey(Entity,related_name='pmiFrom')
    toEntity = models.ForeignKey(Entity,related_name='pmiTo')
    value = models.FloatField()

    def __unicode__(self):
        return self.fromEntity.name +","+ self.toEntity.name +"=>"+ unicode(self.value)
    
class Category(models.Model):
    name = models.CharField(max_length=200)

    def __unicode__(self):
        return self.name

class CategoryScore(models.Model):
    category = models.ForeignKey(Category)
    entity = models.ForeignKey(Entity)
    value = models.FloatField()

    def __unicode__(self):
        return self.category.name + ': ' + self.entity.name + ' - ' + unicode(self.value)
