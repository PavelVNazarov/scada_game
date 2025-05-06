# accounts/urls.py
from django.urls import path
from .views import *

urlpatterns = [
    path('', welcome_view, name='welcome'),  # главная страница
    path("login/", custom_login, name="login"),
    path("dashboard/", dashboard, name="dashboard"),
    path('list', employee_list, name='employee_list'),
    path('new/', employee_create, name='employee_create'),
    path('<int:pk>/edit/', employee_edit, name='employee_edit'),
    path('<int:pk>/delete/', employee_delete, name='employee_delete'),
    path('questions_list', questions_list, name='questions_list'),
]
