from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'vehicles'

urlpatterns = [
    path('standardsearch/', views.standardsearch, name='standardsearch'),
    path('filter/', views.filter, name='filter'),
    path('detail/<int:pk>/', views.detail, name='detail'),
    path('category/<str:category>/', views.category_list, name='category'),
]

# ✅ Serve media files (vehicle images) during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
