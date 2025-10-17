from django.urls import path
from . import views
app_name='Main'

urlpatterns = [
    path('', views.index, name='home'),     
    path('faq/', views.faq, name='faq'),
    path('aboutus/', views.aboutus_view, name='aboutus'),
]
