from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from email_hash import views

urlpatterns = [
    path('start_new_analysis/', views.newsletter_singup, name='new_analysis'),
    path('cancel_analysis/', views.newsletter_unsubscribe,
         name='cancel_analysis'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
