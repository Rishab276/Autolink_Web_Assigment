from django.urls import path
from . import views

urlpatterns = [
    path('', views.standardsearch, name='Vehicles'),
]

