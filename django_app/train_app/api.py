from django.urls import path
from .api_views import trains_root

urlpatterns = [
    path('', trains_root)
]