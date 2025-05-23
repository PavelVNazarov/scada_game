# game/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.db import transaction
from django.urls import reverse
from .models import Question, Answer, EquipmentState, PlayerProgress
from accounts.models import EmployeeProfile

def game_home(request):
    # return redirect('factory_entry')
    return redirect('start_game')

@login_required
@user_passes_test(lambda u: hasattr(u, 'employeeprofile') and u.employeeprofile.is_student())
def factory_entry(request):
    """Основной игровой интерфейс завода"""
    try:
        user_profile = request.user.employeeprofile
    except EmployeeProfile.DoesNotExist:
        return redirect('dashboard')

    # Создаем начальное состояние если не существует
    initial_state, _ = EquipmentState.objects.get_or_create(
        name='Завод отключен',
        defaults={'order': 0, 'description': 'Исходное состояние'}
    )

    # Получаем или создаем прогресс игрока
    player, created = PlayerProgress.objects.get_or_create(
        user=user_profile,
        defaults={'current_state': initial_state}
    )

    # Если current_state отсутствует, устанавливаем начальное состояние
    if not player.current_state:
        player.current_state = initial_state
        player.save()

    # Обработка запуска системы
    if request.method == 'POST' and 'start_system' in request.POST:
        with transaction.atomic():
            section1, _ = EquipmentState.objects.get_or_create(
                name='Участок 1',
                defaults={'order': 1, 'description': 'Первичная активация'}
            )
            player.current_state = section1
            player.attempts = 3
            player.is_failed = False
            player.save()
        return redirect('game:factory_entry')

    # Получаем текущий вопрос для состояния
    current_question = Question.objects.filter(
        equipment_state=player.current_state
    ).prefetch_related('answer_set').first()

    context = {
        'player': player,
        'question': current_question,
        'equipment_states': EquipmentState.objects.order_by('order'),
    }
    return render(request, 'game/factory_entry.html', context)

@require_POST
@login_required
@transaction.atomic
def check_answer(request):
    """Проверка ответа через AJAX"""
    player = get_object_or_404(PlayerProgress, user__user=request.user)
    answer_id = request.POST.get('answer_id')

    if not answer_id:
        return JsonResponse({'error': 'Missing answer_id'}, status=400)

    try:
        answer = Answer.objects.select_related('question').get(pk=answer_id)
        is_correct = answer.is_correct

        if is_correct:
            next_state = EquipmentState.objects.filter(
                order__gt=player.current_state.order
            ).order_by('order').first()

            if next_state:
                player.current_state = next_state
                status = 'success'
                message = 'Правильный ответ! Переходим к следующему этапу.'
            else:
                status = 'completed'
                message = 'Все этапы пройдены! Завод работает стабильно.'
        else:
            player.attempts -= 1
            if player.attempts <= 0:
                player.is_failed = True
                status = 'failed'
                message = 'Авария! Превышено количество попыток.'
            else:
                status = 'error'
                message = f'Неверно! Осталось попыток: {player.attempts}'

        player.save()
        return JsonResponse({
            'status': status,
            'message': message,
            'attempts': player.attempts,
            'next_url': reverse('game:factory_entry') if status == 'success' else None
        })

    except Answer.DoesNotExist:
        return JsonResponse({'error': 'Invalid answer'}, status=400)

@login_required
def section_view(request, section_id):
    """Управление участками завода"""
    player = get_object_or_404(PlayerProgress, user__user=request.user)
    section = get_object_or_404(EquipmentState, pk=section_id)

    if section.order > player.current_state.order + 1:
        return redirect('game:factory_entry')

    # Получаем связанные с участком вопросы
    questions = Question.objects.filter(
        equipment_state=section
    ).prefetch_related('answer_set')

    # Логика активации оборудования
    if request.method == 'POST' and 'activate' in request.POST:
        player.current_state = section
        player.save()
        return redirect('game:factory_entry')

    return render(request, 'game/section_detail.html', {
        'section': section,
        'questions': questions,
        'player': player
    })

@login_required
def game_over(request):
    """Экран завершения игры"""
    player = get_object_or_404(PlayerProgress, user__user=request.user)
    return render(request, 'game/game_over.html', {
        'player': player,
        'state': player.current_state
    })

@login_required
@transaction.atomic
def reset_game(request):
    """Сброс прогресса игры"""
    player = get_object_or_404(PlayerProgress, user__user=request.user)
    initial_state = EquipmentState.objects.get(name='Завод отключен')
    player.current_state = initial_state
    player.attempts = 3
    player.is_failed = False
    player.save()
    return redirect('game:factory_entry')

@login_required
def start_factory(request):
    # Инициализация прогресса
    player, created = PlayerProgress.objects.get_or_create(
        user=request.user.employeeprofile,
        defaults={'current_state': EquipmentState.objects.first()}
    )
    return redirect('game:current_stage')

@login_required
def current_stage(request):
    player = request.user.employeeprofile.playerprogress
    context = {'stage': player.current_state}

    if request.method == 'POST':
        if 'answer' in request.POST:
            answer = request.POST.get('answer', '').strip()
            if answer.lower() == player.current_state.question.correct_answer.lower():
                if player.current_state.next_stage:
                    player.current_state = player.current_state.next_stage
                    player.save()
                else:
                    player.is_completed = True
                    player.save()
            else:
                player.attempts -= 1
                if player.attempts <= 0:
                    player.is_failed = True
                player.save()

    return render(request, 'game/stage.html', context)

@login_required
def final_result(request):
    player = request.user.employeeprofile.playerprogress
    return render(request, 'final.html', {'player': player})

def start_game(request):
    return render(request, 'game.html')

def preparation_page(request):
    return render(request, 'preparation.html')

def equipment_page(request):
    return render(request, 'equipment.html')

def high_temperature_page(request):
    return render(request, 'high_temperature.html')

def final_page(request):
    return render(request, 'final.html')

