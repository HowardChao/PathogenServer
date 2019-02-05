from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from VirusRNASeq import views
from django.contrib.auth import views as auth_views
from email_hash import views
from tmpuser import views

urlpatterns = [
    path('start-new-project/', views.start_new_project, name='start_new_project'),
    # path('profile/', tmp_user_views.profile, name='profile'),
    # path('login/', tmp_user_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    # path('logout/', tmp_user_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),
    # path('password-reset/',
    #      tmp_user_views.PasswordResetView.as_view(
    #          template_name='users/password_reset.html'),
    #      name='password_reset'),
    # path('password-reset-done/',
    #      tmp_user_views.PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'), name='password_reset_done'),
    # path('password-reset-confirm/<uidb64>/<token>/',
    #      tmp_user_views.PasswordResetConfirmView.as_view(
    #          template_name='users/password_reset_confirm.html'),
    #      name='password_reset_confirm'),
    # path('password-reset-complete/',
    #      tmp_user_views.PasswordResetCompleteView.as_view(
    #          template_name='users/password_reset_complete.html'),
    #      name='password_reset_complete'),
    # path('progressbarupload/', include('progressbarupload.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
