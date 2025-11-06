from django.urls import path
from . import views

urlpatterns = [
    path('', views.review_page, name='review_page'),
    path('report/', views.report_page, name='report_page'),
    path('submit/', views.submit_review, name='submit_review'),
    path('submit-report/', views.submit_report, name='submit_report'),
    path('recommendations/', views.recommendations_view, name='recommendations'),
]