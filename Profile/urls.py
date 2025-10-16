from django.urls import path
from . import views

urlpatterns = [
    path('savedvehicles/', views.saved_vehicles, name='savedvehicles'),
]
