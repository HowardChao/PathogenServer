# -*- coding: utf-8 -*-
from email_hash import views
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from django.conf.urls import url
from progressbarupload.views import upload_progress

urlpatterns = [
    path('upload_progress/', upload_progress, name='upload_progress'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
