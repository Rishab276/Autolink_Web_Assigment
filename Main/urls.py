from django.urls import path
from . import views

urlpatterns = [
    path('', views.Main, name='Main'),
]

urlpatterns = [
    path("", views.index, name="home"),     # /
    path("faq/", views.faq, name="faq"),    # /faq/
]

urlpatterns = [
    path('aboutus/', views.aboutus_view, name='aboutus'),
]
