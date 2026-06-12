from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.utils.dateparse import parse_time
from .models import MenuItem, Category, BarItem, KidsItem, BarCategory, KidsCategory, Reservation, Table, UserProfile
from .forms import UserRegistrationForm, ReservationForm

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


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация успешна!')
            return redirect('core:profile')
    else:
        form = UserRegistrationForm()
    return render(request, 'auth/register.html', {'form': form})

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

def hall_view(request):
    tables = Table.objects.filter(is_active=True)
    return render(request, 'hall.html', {'tables': tables})

def api_tables(request):
    """Отдает список столов для карты"""
    tables = Table.objects.filter(is_active=True)
    data = [{'id': t.id, 'number': t.number, 'x': t.pos_x, 'y': t.pos_y} for t in tables]
    return JsonResponse(data, safe=False)

def api_slots(request):
    """Отдает статус слотов для конкретного стола"""
    table_id = request.GET.get('table')
    date = request.GET.get('date')
    
    # Генерируем тайминги (11-13, 13-15 и т.д.)
    times = ["10:00", "12:00", "14:00", "16:00", "18:00", "20:00"]    
    # Смотрим, какие слоты уже заняты
    # Примечание: time здесь это начало слота
    busy_slots_query = Reservation.objects.filter(
        table_id=table_id, 
        date=date, 
        status__in=['confirmed', 'pending']
    ).values_list('time', flat=True)
    
    # Преобразуем datetime.time в строки формата "HH:MM" для точного сравнения
    busy_slots = [t.strftime('%H:%M') for t in busy_slots_query if t]
    
    result = []
    for t in times:
        # Формируем интервал: 10:00 → 10:00-12:00
        start_hour = int(t.split(':')[0])
        end_hour = start_hour + 2
        result.append({
            'time': f"{t}-{end_hour:02d}:00",  # Например: "10:00-12:00"
            'is_busy': t in busy_slots
        })
        
    return JsonResponse(result, safe=False)

def api_tables_status(request):
    """Отдает список ID столов, которые полностью заняты на выбранную дату (все слоты заняты)"""
    date_str = request.GET.get('date')
    if not date_str:
        return JsonResponse([], safe=False)
    
    # Все активные столы
    tables = Table.objects.filter(is_active=True)
    times = ["10:00", "12:00", "14:00", "16:00", "18:00", "20:00"]
    
    # Получаем бронирования на эту дату
    reservations = Reservation.objects.filter(
        date=date_str,
        status__in=['confirmed', 'pending']
    ).values('table_id', 'time')
    
    # Сгруппируем по столу
    from collections import defaultdict
    table_bookings = defaultdict(set)
    for res in reservations:
        if res['time'] and res['table_id']:
            time_str = res['time'].strftime('%H:%M')
            table_bookings[res['table_id']].add(time_str)
            
    busy_table_ids = []
    for table in tables:
        booked_slots = table_bookings[table.id]
        if len(booked_slots) >= len(times) and all(t in booked_slots for t in times):
            busy_table_ids.append(table.id)
            
    return JsonResponse(busy_table_ids, safe=False)

def init_hall_tables(request):
    """Запусти один раз: /admin/init-hall/"""
    from .models import Table
    if Table.objects.exists():
        return HttpResponse("Столы уже созданы.")
        
    # Приблизительные координаты (X%, Y%) под твою схему
    tables_data = [
        # Нижний ряд (справа налево)
        {'n': '1', 'x': 88, 'y': 88, 's': 6}, {'n': '2', 'x': 76, 'y': 88, 's': 6},
        {'n': '3', 'x': 64, 'y': 88, 's': 6}, {'n': '4', 'x': 52, 'y': 88, 's': 6},
        {'n': '5', 'x': 40, 'y': 88, 's': 6}, {'n': '6', 'x': 28, 'y': 88, 's': 6},
        # Ряд выше
        {'n': '7', 'x': 84, 'y': 72, 's': 4}, {'n': '8', 'x': 72, 'y': 72, 's': 4},
        {'n': '9', 'x': 60, 'y': 72, 's': 4}, {'n': '10', 'x': 48, 'y': 72, 's': 4},
        # Центр
        {'n': '11', 'x': 86, 'y': 55, 's': 4}, {'n': '12', 'x': 74, 'y': 58, 's': 4},
        {'n': '13', 'x': 62, 'y': 60, 's': 4}, {'n': '14', 'x': 76, 'y': 48, 's': 4},
        {'n': '15', 'x': 64, 'y': 50, 's': 4}, {'n': '16', 'x': 52, 'y': 52, 's': 4},
        {'n': '17', 'x': 42, 'y': 55, 's': 2},
        # Верхний центр
        {'n': '18', 'x': 82, 'y': 38, 's': 4}, {'n': '19', 'x': 70, 'y': 40, 's': 4},
        {'n': '20', 'x': 58, 'y': 40, 's': 4}, {'n': '21', 'x': 46, 'y': 40, 's': 4},
        # Верхний ряд
        {'n': '22', 'x': 88, 'y': 22, 's': 6}, {'n': '23', 'x': 76, 'y': 22, 's': 6},
        {'n': '24', 'x': 64, 'y': 22, 's': 6}, {'n': '25', 'x': 52, 'y': 22, 's': 6},
        {'n': '26', 'x': 40, 'y': 22, 's': 6}, {'n': '27', 'x': 28, 'y': 22, 's': 6},
        # VIP
        {'n': 'VIP 1', 'x': 92, 'y': 65, 's': 8}, {'n': 'VIP 2', 'x': 92, 'y': 45, 's': 8},
    ]
    
    for t in tables_data:
        Table.objects.create(number=t['n'], seats=t['s'], pos_x=t['x'], pos_y=t['y'])
        
    return HttpResponse(f"✅ Создано {Table.objects.count()} столов. Настрой координаты в админке, если нужно.")

def reservation(request):
    tables = Table.objects.filter(is_active=True)

    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            res_instance = form.save(commit=False)
            if request.user.is_authenticated:
                res_instance.user = request.user
            res_instance.save()
            messages.success(request, 'Столик забронирован! Мы свяжемся с вами.')
            return redirect('core:profile')
        else:
            for error in form.non_field_errors():
                messages.error(request, error)
    else:
        initial = {}
        if request.GET.get('table'):
            initial['table'] = request.GET.get('table')
        if request.GET.get('date'):
            initial['date'] = request.GET.get('date')
        if request.GET.get('time'):
            initial['time'] = request.GET.get('time')
        form = ReservationForm(initial=initial)

    context = {
        'form': form,
        'tables': tables,
        'preselected_table': request.GET.get('table') or request.POST.get('table'),
        'preselected_date': request.GET.get('date') or request.POST.get('date'),
        'preselected_time': request.GET.get('time') or request.POST.get('time'),
    }
    
    return render(request, 'reservation.html', context)