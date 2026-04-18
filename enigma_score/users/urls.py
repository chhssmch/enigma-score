from django.urls import path
from . import views
from django.contrib.auth.views import LoginView, LogoutView 
from .views import register, profile_view, clear_history
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy

app_name = 'users'

urlpatterns = [
    path('profile/', profile_view, name='profile'),
    path('register/', register, name='register'), 
    path('login/', LoginView.as_view(template_name='users/login.html'), name='login'), 
    path('logout/', LogoutView.as_view(), name='logout'),
    path('clear-history/', clear_history, name='clear_history'),
    path(
        'password-reset/',
        auth_views.PasswordResetView.as_view(
            template_name='users/password_reset.html',
            email_template_name='users/password_reset_email.html',  # свой шаблон письма
            success_url= reverse_lazy('users:password_reset_done'),
        ),
        name='password_reset',
    ),
    path(
        'password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='users/password_reset_done.html'
        ),
        name='password_reset_done',
    ),
    path(
        'password-reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='users/password_reset_confirm.html',
            success_url=reverse_lazy('users:password_reset_complete'),
        ),
        name='password_reset_confirm',
    ),
    path(
        'password-reset/complete/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='users/password_reset_complete.html'
        ),
        name='password_reset_complete',
    ),

]