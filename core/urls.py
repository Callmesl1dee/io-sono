from django.urls import path
from . import views

# Важно! Это имя приложения для namespace
app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('menu/', views.menu, name='menu'),
    path('bar/', views.bar_menu, name='bar_menu'),  # ← Проверь эту строку!
    path('kids/', views.kids_menu, name='kids_menu'),
    path('reservation/', views.reservation, name='reservation'),
]