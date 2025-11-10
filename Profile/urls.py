from django.urls import path
from . import views

app_name = 'profile'

urlpatterns = [
    path('', views.profile_view, name='profile'),
    path('save/<int:vehicle_id>/', views.save_vehicle, name='save_vehicle'),
    path('remove/<int:vehicle_id>/', views.remove_saved_vehicle, name='remove_saved_vehicle'),
    path('toggle-save/<int:vehicle_id>/', views.toggle_save, name='toggle_save'),
    path('profile/', views.profile_view, name='profile'),
    path('remove_uploaded_vehicle/<int:vehicle_id>/', views.remove_uploaded_vehicle, name='remove_uploaded_vehicle'),
]
