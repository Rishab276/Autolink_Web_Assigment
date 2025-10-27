#byhumaa
from django.urls import path
from . import views
<<<<<<< HEAD

app_name = 'Reviews'

=======
app_name = 'reviews'
>>>>>>> 34401a921ca0ed74eb2819b1574a3fc115f044ae
urlpatterns = [
    path('', views.review_page, name='review_page'),
    path('report/', views.report_page, name='report_page'),
    path('submit/', views.submit_review, name='submit_review'),
    path('report/submit/', views.submit_report, name='submit_report'),
    path('recommendations/', views.recommendations_view, name='recommendations'),
]