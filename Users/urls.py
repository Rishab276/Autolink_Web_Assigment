# bhewa vigneshwar 2411725
from django.urls import path
from . import views
app_name='users'
urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('registerdetails/', views.registerdetails_view, name='registerdetails'),
    path('sellerRenterdetails/', views.sellerRenterdetails_view, name='sellerRenterdetails'),
    path('sellerRenterdetails/<str:role>/', views.sellerRenterdetails_view, name='sellerRenterdetails_with_role'),
    path('uploadvehicles/', views.uploadvehicles_view, name='uploadvehicles'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
]
