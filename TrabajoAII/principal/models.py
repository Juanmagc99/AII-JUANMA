
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models.aggregates import Min
from django.db.models.base import Model

# Create your models here.

class Tag(models.Model):
    value = models.CharField(max_length=30)

    def __str__(self):
        return self.value

class Job(models.Model):
    title = models.CharField(max_length=250)
    location = models.CharField(max_length=100)
    salary = models.CharField(max_length=100)
    type = models.CharField(max_length=200)
    tags = models.ManyToManyField(Tag)
    url = models.CharField(max_length=70)

    def __str__(self):
        return self.title + "/"  + self.location + "/" + self.salary
