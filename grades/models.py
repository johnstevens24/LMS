from django.db import models
from django.contrib.auth.models import User, Group

# Create your models here.
class Assignment (models.Model):
    title = models.CharField(max_length=200, blank=False)
    description = models.TextField(blank=True)
    deadline = models.DateTimeField(blank=False)
    weight = models.IntegerField(blank=False)
    points = models.IntegerField(blank=False)

class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, blank=False)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    grader = models.ForeignKey(User, related_name='graded_set', null=True, on_delete=models.SET_NULL, blank=True)
    file = models.FileField(blank=False)
    score = models.FloatField(blank=True, null=True)
    