from django.db import models

class Book(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.TextField()
    author = models.TextField()
    area = models.TextField()
    genre = models.TextField()
    price = models.FloatField()

