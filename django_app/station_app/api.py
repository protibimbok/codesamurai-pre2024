from django.urls import path
from .api_views import stations_root

urlpatterns = [
    path('', stations_root)
]