from django.urls import path
from . import views

urlpatterns = [
    path('', views.Reviews, name='Reviews'),
]
