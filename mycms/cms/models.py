from __future__ import unicode_literals

from django.db import models

# Create your models here.

class webinfo(models.Model):
    title=models.CharField(max_length=32)
    name=models.CharField(max_length=32)
    home=models.CharField(max_length=32)
    contact=models.CharField(max_length=32)
    about=models.CharField(max_length=32)
    def __str__(self):
        return self.title

class carousel(models.Model):
    carousel_title=models.CharField(max_length=32)
    carousel_content=models.TextField(max_length=255)
    def __str__(self):
        return self.carousel_title
    
class introduction(models.Model):
    heading=models.CharField(max_length=32)
    introduction=models.TextField(max_length=255)
    def __str__(self):
        return self.heading
    
class feature(models.Model):
    feature_heading=models.CharField(max_length=32)
    feature_muted=models.CharField(max_length=32)
    feature_lead=models.TextField(max_length=255)
    def __str__(self):
        return self.feature_heading
    
    
    
    