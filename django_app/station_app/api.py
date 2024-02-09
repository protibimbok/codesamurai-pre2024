from django.urls import path
from .api_views import stations_root, station_trains

urlpatterns = [
    path('', stations_root),
    path('/<int:station_id>/trains', station_trains)
]