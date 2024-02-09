from django.db import models

# Create your models here.
class User(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.TextField()
    author = models.TextField()
    genre = models.TextField()
    price = models.FloatField()
