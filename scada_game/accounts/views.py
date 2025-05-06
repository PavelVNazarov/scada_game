# accounts/views.py
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from .models import EmployeeProfile
from .forms import EmployeeForm

def is_superadmin(user):
    return user.is_superuser

@user_passes_test(is_superadmin)
def employee_list(request):
    employees = User.objects.filter(is_superuser=False).select_related('employeeprofile').all()
    return render(request, 'list.html', {'employees': employees})

@user_passes_test(is_superadmin)
def employee_create(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            user = form.save()
            EmployeeProfile.objects.create(
                user=user,
                contact=form.cleaned_data['contact'],
                role=form.cleaned_data['role']
            )
            return redirect('employee_list')
    else:
        form = EmployeeForm()
    return render(request, 'form.html', {'form': form})

@user_passes_test(is_superadmin)
def employee_edit(request, pk):
    user = get_object_or_404(User, pk=pk)
    if user.is_superuser:
        return redirect('employee_list')  # или вывести ошибку
    profile = user.employeeprofile
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            profile.contact = form.cleaned_data['contact']
            profile.role = form.cleaned_data['role']
            profile.save()
            return redirect('employee_list')
    else:
        form = EmployeeForm(instance=user, initial={
            'contact': profile.contact,
            'role': profile.role
        })
    return render(request, 'form.html', {'form': form})

@user_passes_test(is_superadmin)
def employee_delete(request, pk):
    employee = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        employee.delete()
        return redirect('employee_list')
    return render(request, 'confirm_delete.html', {'employee': employee})

def welcome_view(request):
    return render(request, 'welcome.html')

def custom_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Проверка заполнения полей
        if not username or not password:
            messages.error(request, "Заполните все поля")
            return redirect("login")

        # Аутентификация
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("dashboard")  # Убедитесь, что 'dashboard' — корректное имя маршрута
        else:
            messages.error(request, "Неверный логин или пароль")

    return render(request, "login.html")

@login_required
def dashboard(request):
    """Основная панель управления"""
    departments = [
        #{'name': 'Завод', 'url': 'factory_entry'}
        {'name': 'Завод', 'url': 'game'}
    ]
    return render(request, 'dashboard.html', {
        'departments': departments,
        'is_superuser': request.user.is_superuser  # Передаем информацию о суперпользователе
    })

def questions_list(request):
    return render(request, 'questions_list.html')


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')
