from django.urls import path
from .api_views import users_root

urlpatterns = [
    path('', users_root)
]