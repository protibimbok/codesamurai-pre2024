from django.db import models
from users_app.models import User
from station_app.models import Station

# Create your models here.
class Ticket(models.Model):
    wallet_id = models.ForeignKey(User, on_delete=models.CASCADE)
    time_after = models.TimeField()
    station_from = models.ForeignKey(Station, on_delete = models.CASCADE, related_name = 'station_from')
    station_to = models.ForeignKey(Station, on_delete = models.CASCADE, related_name = 'station_to')