from django.urls import path
from . import views
from .views import CustomPasswordChangeView

app_name = 'profile'

urlpatterns = [
    path('', views.profile_view, name='profile'),
    path('profile/', views.profile_view, name='profile'),
    path('save/<int:vehicle_id>/', views.save_vehicle, name='save_vehicle'),
    path('remove/<int:vehicle_id>/', views.remove_saved_vehicle, name='remove_saved_vehicle'),
    path('toggle-save/<int:vehicle_id>/', views.toggle_save, name='toggle_save'),
    path('remove_uploaded_vehicle/<int:vehicle_id>/', views.remove_uploaded_vehicle, name='remove_uploaded_vehicle'),
    path('toggle-sold/<int:vehicle_id>/', views.toggle_sold, name='toggle_sold'),
    path('vehicle/<int:vehicle_id>/toggle_rented/', views.toggle_rented, name='toggle_rented'),
    path('password_change/', CustomPasswordChangeView.as_view(), name='passwordchange'),
    path('ajax-unsave/<int:vehicle_id>/', views.ajax_unsave_vehicle, name='ajax_unsave'),
    path('ajax-weather/<int:vehicle_id>/', views.ajax_vehicle_weather, name='ajax_weather'),
]