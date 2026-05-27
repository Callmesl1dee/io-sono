from django.contrib import admin
from django.contrib.admin import AdminSite
from django.urls import reverse
from django.utils import timezone
from django.db.models import Sum
from .models import Category, MenuItem, Reservation, BarCategory, BarItem, KidsCategory, KidsItem

# === КАСТОМНЫЙ ADMINSITE ===
class CustomAdminSite(AdminSite):
    site_header = "IO SONO — Админка"
    site_title = "IO SONO Admin"
    index_title = "Администрирование сайта"
    
    def index(self, request, extra_context=None):
        """Переопределяем главную страницу админки"""
        
        # === Статистика на сегодня ===
        today = timezone.now().date()
        
        # Всего гостей сегодня
        today_guests = Reservation.objects.filter(date=today).aggregate(
            total=Sum('guests')
        )['total'] or 0
        
        # Количество броней сегодня
        today_bookings = Reservation.objects.filter(date=today).count()
        
        # Забронированные столики
        reserved_tables = today_bookings
        
        # Общая статистика
        total_users = Reservation.objects.values('user').distinct().count()
        
        extra_context = extra_context or {}
        extra_context.update({
            'today_guests': today_guests,
            'today_bookings': today_bookings,
            'reserved_tables': reserved_tables,
            'total_users': total_users,
            'analytics_url': reverse('admin_analytics'),
        })
        
        return super().index(request, extra_context)

# Создаём экземпляр кастомного сайта
admin_site = CustomAdminSite(name='admin')


# === РЕГИСТРАЦИЯ МОДЕЛЕЙ (правильный синтаксис для кастомного AdminSite) ===

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'is_featured')
    list_filter = ('category', 'is_featured')
    search_fields = ('name', 'description')

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'date', 'time', 'guests', 'status', 'created_at')
    list_filter = ('date', 'status', 'guests')
    readonly_fields = ('created_at',)
    ordering = ['-created_at']

@admin.register(BarCategory)
class BarCategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ('name', 'order')

@admin.register(BarItem)
class BarItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'bar_type', 'price', 'is_featured')
    list_filter = ('bar_type', 'category', 'is_featured')
    search_fields = ('name', 'description')

@admin.register(KidsCategory)
class KidsCategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}

@admin.register(KidsItem)
class KidsItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'is_popular')
    list_filter = ('category', 'is_popular')
    search_fields = ('name', 'description')


# === РЕГИСТРИРУЕМ ВСЕ МОДЕЛИ В КАСТОМНОМ САЙТЕ ===
# Это связывает наши Admin-классы с custom admin_site
admin_site.register(Category, CategoryAdmin)
admin_site.register(MenuItem, MenuItemAdmin)
admin_site.register(Reservation, ReservationAdmin)
admin_site.register(BarCategory, BarCategoryAdmin)
admin_site.register(BarItem, BarItemAdmin)
admin_site.register(KidsCategory, KidsCategoryAdmin)
admin_site.register(KidsItem, KidsItemAdmin)