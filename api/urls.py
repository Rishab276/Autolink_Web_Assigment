from django.urls import path
from Vehicles.views import standardsearch  # 👈 import from Vehicles app
from Vehicles.views import VehicleListAPI

urlpatterns = [
    path('vehicles/', VehicleListAPI.as_view(), name='vehicle-list-api'),
]