import datetime

from django.db import models


class SingletonModel(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super(SingletonModel, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


class ParserUpdaterInfo(SingletonModel):
    last_updated = models.DateTimeField(default=datetime.datetime.now())


class Profession(models.Model):
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    description = models.TextField()
    skills = models.ManyToManyField("Skill")
    id_from_site = models.IntegerField(blank=True, null=True)


class Skill(models.Model):
    name = models.CharField(max_length=200, blank=True, null=True)
    level = models.IntegerField(blank=True, null=True)
    color = models.CharField(max_length=20, blank=True, null=True)
