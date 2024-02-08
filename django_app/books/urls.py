from django.urls import path
from .views import get_or_add_books, update_book

urlpatterns = [
    path("", get_or_add_books),
    path("<int:id>", update_book),
]
