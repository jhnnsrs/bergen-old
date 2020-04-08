from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from elements.models import Experiment, Sample, Transformation, ROI
from larvik.models import LarvikConsumer, LarvikJob
from test.models import *

class Tester(LarvikConsumer):

    def __str__(self):
        return "Tester at Path {1}".format(self.name, self.channel)

class Testing(LarvikJob):
    tester = models.ForeignKey(Tester, on_delete=models.CASCADE)

    def __str__(self):
        return "Test for Testing: {0}".format(self.tester.name)