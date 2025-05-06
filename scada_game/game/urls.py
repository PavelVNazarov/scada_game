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
    # path('reset-game/', reset_game, name='reset_game'),
    # path('start/', start_factory, name='start_factory'),
    path('stage/', current_stage, name='current_stage'),
    path('result/', final_result, name='final_result'),
    path('reset/', reset_game, name='reset_game'),
    path('start/', start_game, name='start_game'),
    path('preparation/', preparation_page, name='preparation_page'),
    path('equipment/', equipment_page, name='equipment_page'),
    path('high-temperature/', high_temperature_page, name='high_temperature_page'),
    path('final/', final_page, name='final_page'),
]

