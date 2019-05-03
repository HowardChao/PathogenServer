from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path
from email_hash import views

urlpatterns = [
    path('start-new-analysis/', views.newsletter_singup, name='new_analysis'),
    path('deleteanalysis/', views.newsletter_unsubscribe,
         name='delete_analysis'),
    path('check-project/', views.check_project, name='check_project'),
    path('help/', views.help_view, name='help'),
    path('about/', views.about_view, name='about'),
    path('merge_project', views.merge_project, name='merge_project'),
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
