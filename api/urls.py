from django.urls import path
from Vehicles.views import VehicleListAPI

urlpatterns = [
    path('vehicles/', VehicleListAPI.as_view(), name='vehicle-list-api'),
]

# api/urls.py
# All REST API endpoints that the Flet mobile app will call.
# Every URL here starts with /api/ (set in the main urls.py)

from django.urls import path
from . import views

urlpatterns = [

    # --- AUTH ---
    # POST /api/login/          → Login with email & password, get a token back
    # POST /api/register/       → Create a new account
    # POST /api/logout/         → Logout (deletes the token)
    # GET  /api/profile/        → Get logged-in user's profile info
    path('login/', views.LoginAPI.as_view(), name='api_login'),
    path('register/', views.RegisterAPI.as_view(), name='api_register'),
    path('logout/', views.LogoutAPI.as_view(), name='api_logout'),
    path('profile/', views.ProfileAPI.as_view(), name='api_profile'),
    path('profile/update/', views.UpdateProfileAPI.as_view(), name='api_profile_update'),

    # --- VEHICLES ---
    # GET /api/vehicles/                → List all vehicles (with optional filters)
    # GET /api/vehicles/<id>/           → Get details of one vehicle
    # GET /api/vehicles/nearby/         → Get vehicles near user's GPS location
    path('vehicles/', views.VehicleListAPI.as_view(), name='api_vehicles'),
    path('vehicles/nearby/', views.NearbyVehiclesAPI.as_view(), name='api_nearby'),
    path('vehicles/<int:pk>/', views.VehicleDetailAPI.as_view(), name='api_vehicle_detail'),
    path('my-vehicles/', views.MyVehiclesAPI.as_view(), name='api_my_vehicles'),
    path('vehicles/upload/', views.UploadVehicleAPI.as_view(), name='api_upload_vehicle'),
    path('vehicles/<int:pk>/update/', views.UpdateVehicleAPI.as_view(), name='api_update_vehicle'),
    path('vehicles/<int:pk>/delete/', views.DeleteVehicleAPI.as_view(), name='api_delete_vehicle'),


    # --- REVIEWS ---
    # GET  /api/reviews/         → List all approved reviews
    # POST /api/reviews/submit/  → Submit a new review
    path('reviews/', views.ReviewListAPI.as_view(), name='api_reviews'),
    path('reviews/submit/', views.ReviewSubmitAPI.as_view(), name='api_review_submit'),

    # --- SAVED VEHICLES ---
    # GET  /api/saved/                      → Get user's saved vehicles
    # POST /api/saved/toggle/<vehicle_id>/  → Save or unsave a vehicle
    path('saved/sorted/', views.SavedVehiclesSortedAPI.as_view(), name='api_saved_sorted'),
    path('saved/', views.SavedVehiclesAPI.as_view(), name='api_saved'),
    path('saved/toggle/<int:vehicle_id>/', views.ToggleSaveAPI.as_view(), name='api_toggle_save'),
]
