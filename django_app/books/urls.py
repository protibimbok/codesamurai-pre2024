from django.urls import path
from .views import get_books, update_book

urlpatterns = [
    path("", get_books),
    path("<int:id>", update_book),
]
