from django.urls import path, include
from users_app.api_views import get_wallet
from ticket_app.api_views import optimal_plan

urlpatterns = [
    path('', include('rest_framework.urls')),
    path('/trains', include('train_app.api')),
    path('/users', include('users_app.api')),
    path('/stations', include('station_app.api')),
    path('/tickets', include('ticket_app.api')),
    path('/wallets/<int:wallet_id>', get_wallet),
    path('/routes', optimal_plan),
]