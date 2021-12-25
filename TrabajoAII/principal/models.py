from django.db import models
from django.db.models.base import Model

# Create your models here.
class Job(models.Model):
    title = models.CharField(max_length=250)
    location = models.CharField(max_length=100)
    salary = models.CharField(max_length=100)
    type = models.CharField(max_length=200)
    advantages = models.CharField(max_length=300)
    skills = models.CharField(max_length=300)

    def __str__(self):
        return self.title + "/"  + self.location + "/" + self.salary