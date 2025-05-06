# game/models.py
from django.db import models
from django.contrib.auth.models import User
from accounts.models import EmployeeProfile


class Question(models.Model):
    text = models.TextField('Вопрос')
    equipment_state = models.ForeignKey('EquipmentState', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.text[:50]


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.CharField('Ответ', max_length=255)
    is_correct = models.BooleanField('Правильный', default=False)


class EquipmentState(models.Model):
    name = models.CharField('Состояние', max_length=100)
    order = models.PositiveIntegerField('Порядок', default=0)
    is_active = models.BooleanField('Активно', default=False)
    description = models.TextField('Описание состояния')

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name

class GameStage(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='stages/')
    next_stage = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    question = models.ForeignKey('Question', on_delete=models.SET_NULL, null=True)
    is_final = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class PlayerProgress(models.Model):
    user = models.OneToOneField('accounts.EmployeeProfile', on_delete=models.CASCADE)
    current_state = models.ForeignKey('EquipmentState', on_delete=models.SET_NULL, null=True)  # Исправлено!
    attempts = models.PositiveIntegerField(default=3)
    is_failed = models.BooleanField(default=False)

    def reset(self):
        self.current_state = EquipmentState.objects.first()
        self.attempts = 3
        self.is_failed = False
        self.save()

class GameEvent(models.Model):
    EVENT_TYPES = (
        ('leak', 'Утечка'),
        ('failure', 'Поломка'),
        ('success', 'Успех'),
        ('warning', 'Предупреждение'),
    )

    title = models.CharField('Событие', max_length=100)
    event_type = models.CharField('Тип', max_length=20, choices=EVENT_TYPES)
    description = models.TextField('Описание')
    trigger_condition = models.TextField('Условие активации')
    effect = models.TextField('Эффект')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_event_type_display()}: {self.title}"


