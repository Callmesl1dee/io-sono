from django.shortcuts import render, redirect
from django.contrib import messages
from .models import MenuItem, Category, BarItem, KidsItem, BarCategory, KidsCategory, Reservation

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
        Reservation.objects.create(
            name=request.POST.get('name'),
            phone=request.POST.get('phone'),
            date=request.POST.get('date'),
            time=request.POST.get('time'),
            guests=request.POST.get('guests', 2)
        )
        messages.success(request, 'Столик забронирован! Мы свяжемся с вами.')
        return redirect('core:reservation')
    
    return render(request, 'reservation.html')