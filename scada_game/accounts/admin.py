# accounts/admin.py:

from django.contrib import admin
from .models import EmployeeProfile
from django.contrib.auth.admin import UserAdmin

admin.site.register(EmployeeProfile)
