# accounts/models.py
from django.db import models
from django.contrib.auth.models import User


class EmployeeProfile(models.Model):
    ROLES = (
        ('student', 'Студент'),
        ('teacher', 'Преподаватель'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    contact = models.CharField('Контакт', max_length=100)
    role = models.CharField('Роль', max_length=20, choices=ROLES)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.role})"

    def is_teacher(self):
        return self.role == 'teacher'

    def is_student(self):
        return self.role == 'student'

User._meta.get_field('username').verbose_name = 'Логин'
User._meta.get_field('first_name').verbose_name = 'Имя'
User._meta.get_field('last_name').verbose_name = 'Фамилия'

