from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from dataanalysis import views

urlpatterns = [
    path('<slug:slug_project>/', views.whole_dataanalysis, name='dataanalysis_home'),
    path('result/<slug:slug_project>/', views.show_result, name="dataanalysis_result"),
    path('result/<slug:slug_project>/overview/',
         views.show_result_overview, name="dataanalysis_result_overview"),
    path('result/<slug:slug_project>/current-status/',
         views.current_status, name="dataanalysis_result_current_status"),
    path('upload-progress/', views.upload_progress, name='upload_progress')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
