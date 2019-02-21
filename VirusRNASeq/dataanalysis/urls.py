from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from dataanalysis import views

urlpatterns = [
    path('<slug:slug_project>/', views.paired_end_upload, name='dataanalysis_home'),
    path('result/<slug:slug_project>/', views.show_result, name="dataanalysis_result"),
    path('result/<slug:slug_project>/overview/',views.show_result_overview, name="dataanalysis_result_overview"),
    path('upload/simple/', views.simple_upload, name='simple_upload'),
    path('upload/form/', views.model_form_upload, name='model_form_upload'),
    path('upload-progress/', views.upload_progress, name='upload_progress')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
