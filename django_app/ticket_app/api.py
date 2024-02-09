from django.urls import path
from .api_views import purchase_ticket

urlpatterns = [
    path('', purchase_ticket)
]