from django.urls import path
from . import views
app_name = 'reviews'
urlpatterns = [
    path('recommendations/', views.recommendations_view, name='recommendations'),
    path('report/', views.report_view, name='report'),
    path('review/', views.review_view, name='review'),
]






# urlpatterns = [
#     path('', views.recommendations, name='recommendations'),
# ]

# urlpatterns = [
#     path('', views.report, name='report'),
# ]

