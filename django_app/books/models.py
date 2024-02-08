from django.db import models

class Books(models.Model):
    title = models.CharField(max_length=5000)
    author = models.CharField(max_length=5000)
    area = models.CharField(max_length=5000)
    genre = models.CharField(max_length=5000)
    price = models.FloatField()

