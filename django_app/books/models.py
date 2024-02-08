from django.db import models

class Books(models.Model):
    title = models.CharField()
    author = models.CharField()
    area = models.CharField()
    genre = models.CharField()
    price = models.FloatField()

