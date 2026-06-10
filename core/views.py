from django.shortcuts import render, redirect
from django.contrib import messages
from .models import MenuItem, Category, BarItem, KidsItem, BarCategory, KidsCategory, Reservation
from .models import UserProfile, Reservation  # Добавь UserProfile сюда

def home(request):
    dishes = MenuItem.objects.select_related('category').filter(is_featured=True)[:6]
    return render(request, 'index.html', {'dishes': dishes})

def menu(request):
    dishes = MenuItem.objects.select_related('category').all()
    categories = Category.objects.prefetch_related('menuitem_set').all()
    return render(request, 'menu.html', {
        'dishes': dishes,
        'categories': categories
    })

def bar_menu(request):
    items = BarItem.objects.select_related('category').all()
    categories = BarCategory.objects.prefetch_related('items').all()
    
    # Группировка по типам
    bar_types = {
        'non_alcoholic': items.filter(bar_type='non_alcoholic'),
        'alcoholic': items.filter(bar_type='alcoholic'),
        'cocktail_classic': items.filter(bar_type='cocktail_classic'),
        'cocktail_author': items.filter(bar_type='cocktail_author'),
    }
    
    return render(request, 'bar_menu.html', {
        'items': items,
        'categories': categories,
        'bar_types': bar_types
    })

def kids_menu(request):
    items = KidsItem.objects.select_related('category').all()
    categories = KidsCategory.objects.prefetch_related('items').all()
    return render(request, 'kids_menu.html', {
        'items': items,
        'categories': categories
    })

def reservation(request):
    from .models import Reservation
    from django.contrib import messages
    from django.shortcuts import redirect
    
    if request.method == 'POST':
        # Получаем данные из формы
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        date = request.POST.get('date')
        time = request.POST.get('time')
        guests = request.POST.get('guests', 2)
        
        # Создаём бронь
        new_reservation = Reservation.objects.create(
            name=name,
            phone=phone,
            date=date,
            time=time,
            guests=guests,
        )
        
        # 🔥 ВАЖНО: Если пользователь залогинен — привязываем бронь к нему
        if request.user.is_authenticated:
            new_reservation.user = request.user
            new_reservation.save()
        
        messages.success(request, 'Столик забронирован! Мы свяжемся с вами.')
        return redirect('core:profile')  # Перенаправляем в профиль, чтобы сразу увидеть бронь
    
    return render(request, 'reservation.html')

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Reservation  # Импортируем модель броней

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Простая проверка
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Пользователь с таким именем уже существует')
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            login(request, user)
            messages.success(request, 'Регистрация успешна!')
            return redirect('core:profile')
            
    return render(request, 'auth/register.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Привет, {username}!')
            return redirect('core:profile') # Перенаправляем в кабинет
        else:
            messages.error(request, 'Неверный логин или пароль')
            
    return render(request, 'auth/login.html')

def logout_view(request):
    logout(request)
    return redirect('core:home')

# В core/views.py

def profile(request):
    if not request.user.is_authenticated:
        return redirect('core:login')
    
    user = request.user
    
    # === ИСПРАВЛЕНИЕ: Создаем профиль, если его нет ===
    try:
        profile = user.profile
    except UserProfile.DoesNotExist:
        # Если профиля нет (старый юзер), создаем его
        profile = UserProfile.objects.create(user=user)
    # ==================================================
    
    # История бронирований
    reservations = Reservation.objects.filter(user=user).order_by('-created_at')
    
    # Подсчет баллов (логика: 100 баллов за каждую подтвержденную бронь)
    confirmed_count = Reservation.objects.filter(user=user, status='confirmed').count()
    expected_points = confirmed_count * 100
    
    # Если баллов в базе меньше, чем должно быть - обновляем
    if profile.bonus_points < expected_points:
        profile.bonus_points = expected_points
        profile.save()

    context = {
        'profile': profile,
        'reservations': reservations,
        'total_spent': reservations.count() * 1500, # Примерная сумма трат (заглушка)
    }
    
    return render(request, 'auth/profile.html', context)
    
    
def download_receipt(request, reservation_id):
    """Возвращает HTML-фрагмент чека для модалки"""
    if not request.user.is_authenticated:
        return redirect('core:login')
    
    try:
        reservation = Reservation.objects.get(id=reservation_id, user=request.user)
    except Reservation.DoesNotExist:
        return redirect('core:profile')
    
    # Данные для чека
    receipt_data = {
        'id': reservation.id,
        'date': reservation.date,
        'time': reservation.time,
        'guests': reservation.guests,
        'status': reservation.get_status_display(),
        'total_price': reservation.guests * 1500,  # Условная цена
        'created': reservation.created_at,
    }
    
    return render(request, 'auth/receipt_modal.html', {'receipt': receipt_data})
    
def loyalty(request):
    if not request.user.is_authenticated:
        return redirect('core:login')
    
    # Пример: считаем баллы (упрощённо)
    points = Reservation.objects.filter(user=request.user, status='confirmed').count() * 10
    
    return render(request, 'auth/loyalty.html', {'points': points})

# === ADMIN ANALYTICS ===
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Sum, F
from django.utils import timezone
from datetime import timedelta, datetime
import json

@staff_member_required
def admin_analytics(request):
    """Дашборд с аналитикой для админки"""
    
    # === 1. Бронирования по дням (за последние 14 дней) ===
    today = timezone.now().date()
    dates = [(today - timedelta(days=i)) for i in range(13, -1, -1)]
    
    bookings_by_day = []
    for date in dates:
        count = Reservation.objects.filter(date=date).count()
        bookings_by_day.append({
            'date': date.strftime('%d.%m'),
            'count': count
        })
    
    # === 2. Топ категорий блюд (по количеству блюд в категории) ===
    # Упрощённо: считаем, сколько блюд в каждой категории
    from .models import Category
    category_stats = Category.objects.annotate(
        items_count=Count('items')  # ← Исправлено: 'items' вместо 'menuitem'
    ).order_by('-items_count')[:5]
    
    top_categories = [
        {'name': cat.name, 'count': cat.items_count} 
        for cat in category_stats
    ]
    
    # === 3. Статистика по статусам ===
    status_stats = Reservation.objects.values('status').annotate(
        count=Count('id')
    ).order_by('status')
    
    status_labels = [s['status'] for s in status_stats]
    status_counts = [s['count'] for s in status_stats]
    
    # === 4. Карточки с метриками ===
    total_bookings = Reservation.objects.count()
    confirmed_bookings = Reservation.objects.filter(status='confirmed').count()
    total_guests = Reservation.objects.aggregate(total=Sum('guests'))['total'] or 0
    avg_guests = round(total_guests / total_bookings, 1) if total_bookings > 0 else 0
    
    # === 5. Брони по количеству гостей (гистограмма) ===
    guests_stats = Reservation.objects.values('guests').annotate(
        count=Count('id')
    ).order_by('guests')
    
    guests_labels = [f"{s['guests']} чел." for s in guests_stats]
    guests_counts = [s['count'] for s in guests_stats]
    
    context = {
        'title': 'Аналитика',
        'bookings_by_day': json.dumps(bookings_by_day),
        'top_categories': json.dumps(top_categories),
        'status_labels': json.dumps(status_labels),
        'status_counts': json.dumps(status_counts),
        'guests_labels': json.dumps(guests_labels),
        'guests_counts': json.dumps(guests_counts),
        'metrics': {
            'total_bookings': total_bookings,
            'confirmed_bookings': confirmed_bookings,
            'total_guests': total_guests,
            'avg_guests': avg_guests,
        }
    }
    
    return render(request, 'admin/analytics.html', context)