from django.db import models
from station_app.models import *

# Create your models here.

class Train(models.Model):
    train_id = models.AutoField(primary_key=True)
    train_name = models.TextField()
    capacity = models.IntegerField()
    

class Stop(models.Model):
    stop_id = models.AutoField(primary_key=True)
    train_id = models.ForeignKey(Train, on_delete=models.CASCADE)
    station_id = models.ForeignKey(Station, on_delete=models.CASCADE)
    arrival_time = models.TextField()
    departure_time = models.TextField()
    fare = models.IntegerField()
