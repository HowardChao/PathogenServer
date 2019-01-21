from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from dataanalysis import views

urlpatterns = [
    path('', views.home, name='home'),
    path('upload/simple/', views.simple_upload, name='simple_upload'),
    path('upload/form/', views.model_form_upload, name='model_form_upload'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
