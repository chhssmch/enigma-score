from django.urls import path
from . import views

app_name = 'credit_score'

urlpatterns = [
    path('', views.home_page, name='home'),
    path('check-credit/', views.check_credit, name='check_credit'),
]

