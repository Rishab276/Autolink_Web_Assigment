#MAIGHUN-2412258
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
    path('mark_as_sold/<int:vehicle_id>/', views.mark_as_sold, name='mark_as_sold'),
    path('unmark_as_sold/<int:vehicle_id>/', views.unmark_as_sold, name='unmark_as_sold'),
    path('vehicle/<int:vehicle_id>/mark_as_rented/', views.mark_as_rented, name='mark_as_rented'),
    path('vehicle/<int:vehicle_id>/unmark_as_rented/', views.unmark_as_rented, name='unmark_as_rented'),
]
