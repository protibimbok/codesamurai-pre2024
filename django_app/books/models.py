from django.db import models

class Books(models.Model):
    title = models.TextField()
    author = models.TextField()
    area = models.TextField()
    genre = models.TextField()
    price = models.FloatField()

