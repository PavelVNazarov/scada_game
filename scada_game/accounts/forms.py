# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import EmployeeProfile

class LoginForm(forms.Form):
    username = forms.CharField(label='Логин', max_length=100)
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)

class EmployeeForm(UserCreationForm):
    # Кастомные метки и сообщения для полей User
    username = forms.CharField(
        label='Имя пользователя',
        error_messages={'unique': 'Пользователь с таким именем уже существует.'}
    )
    password1 = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput,
        help_text='Пароль должен содержать минимум 8 символов.'
    )
    password2 = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput,
        help_text='Введите пароль ещё раз для проверки.'
    )
    first_name = forms.CharField(label='Имя')
    last_name = forms.CharField(label='Фамилия')

    # Поля EmployeeProfile
    contact = forms.CharField(label='Контактная информация')
    role = forms.ChoiceField(label='Роль', choices=EmployeeProfile.ROLES)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'password1', 'password2', 'contact', 'role']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            # Проверяем, существует ли пользователь с таким именем
            if self.instance and self.instance.username == username:
                # Если это тот же пользователь, не выдаем ошибку
                return username
            raise forms.ValidationError('Пользователь с таким именем уже существует.')
        return username

    # Переопределение сообщения о несовпадении паролей
    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Пароли не совпадают!")
        return password2
