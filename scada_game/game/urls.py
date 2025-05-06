# game/urls.py
from django.urls import path
from .views import *

# app_name = 'game'
urlpatterns = [
    path('', game_home, name='game'),
    path('factory/', factory_entry, name='factory_entry'),
    path('check-answer/', check_answer, name='check_answer'),
    path('section/<int:section_id>/', section_view, name='section_detail'),
    path('game-over/', game_over, name='game_over'),
    path('reset-game/', reset_game, name='reset_game'),
]

