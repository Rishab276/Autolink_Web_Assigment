from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('registerdetails/', views.registerdetails_view, name='registerdetails'),
    path('sellerRenterdetails/', views.sellerRenterdetails_view, name='sellerRenterdetails'),
    path('uploadvehicles/', views.uploadvehicles_view, name='uploadvehicles'),
]