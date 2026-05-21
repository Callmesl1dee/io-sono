from django.shortcuts import render
from .models import MenuItem

def home(request):
    # Берем все блюда из базы данных
    dishes = MenuItem.objects.all()
    
    # Отправляем их в файл index.html
    return render(request, 'index.html', {'dishes': dishes})