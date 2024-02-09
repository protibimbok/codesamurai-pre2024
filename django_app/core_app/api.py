from django.urls import path, include


urlpatterns = [
    path('', include('rest_framework.urls')),
    path('/trains', include('train_app.api')),
    path('/users', include('train_app.api')),
    path('/stations', include('train_app.api')),
    path('/tickets', include('ticket_app.api')),
]