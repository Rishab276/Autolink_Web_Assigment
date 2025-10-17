from django.urls import path
from . import views

urlpatterns = [
    path('savedvehicles/', views.saved_vehicles, name='savedvehicles'),
    path('save/<int:vehicle_id>/', views.save_vehicle, name='save_vehicle'),
    path('remove/<int:vehicle_id>/', views.remove_saved_vehicle, name='remove_saved_vehicle'),
    path('toggle_save/<int:vehicle_id>/', views.toggle_save_vehicle, name='toggle_save_vehicle'),
    path('profile/', views.profile_view, name='profile'),
    path('remove_uploaded_vehicle/<int:vehicle_id>/', views.remove_uploaded_vehicle, name='remove_uploaded_vehicle'),
]

