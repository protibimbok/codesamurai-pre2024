from django.urls import path, include


urlpatterns = [
    path('', include('rest_framework.urls')),
    path('/trains', include('train_app.api')),
    path('/users', include('users_app.api')),
    path('/stations', include('station_app.api')),
    path('/tickets', include('ticket_app.api')),
]