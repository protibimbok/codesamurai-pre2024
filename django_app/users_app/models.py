from django.db import models

# Create your models here.

class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    user_name = models.TextField()
    balance = models.IntegerField()