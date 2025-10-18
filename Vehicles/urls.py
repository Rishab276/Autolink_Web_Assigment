#bysalwan
from django.urls import path
from . import views

app_name = 'vehicles'

urlpatterns = [
    path('standardsearch/', views.standardsearch, name='standardsearch'),
    path('filter/', views.filter, name='filter'),
    path('detail/<int:pk>/', views.detail, name='detail'),
]

