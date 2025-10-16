from django.urls import path
from . import views


urlpatterns = [
    path('', views.standardsearch, name='Vehicles'),
    path('filter/', views.filter, name='filter'),
    path('detail/<int:pk>/', views.detail, name='detail'),
]



