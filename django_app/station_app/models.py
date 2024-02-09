from django.db import models

# Create your models here.


class Station(models.Model):
    station_id = models.AutoField(primary_key=True)
    station_name = models.TextField()
    longitude = models.FloatField()
    latitude = models.FloatField()