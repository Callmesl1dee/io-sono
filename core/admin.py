from django.contrib import admin
from django.contrib.admin import AdminSite
from django.urls import reverse
from django.utils import timezone
from django.db.models import Sum
from django.utils.html import format_html, mark_safe
from .models import Category, MenuItem, Reservation, BarCategory, BarItem, KidsCategory, KidsItem, Table

# === КАСТОМНЫЙ ADMINSITE ===
class CustomAdminSite(AdminSite):
    site_header = "IO SONO — Админка"
    site_title = "IO SONO Admin"
    index_title = "Администрирование сайта"
    
    def index(self, request, extra_context=None):
        """Переопределяем главную страницу админки"""
        today = timezone.now().date()
        
        today_guests = Reservation.objects.filter(date=today).aggregate(total=Sum('guests'))['total'] or 0
        today_bookings = Reservation.objects.filter(date=today).count()
        reserved_tables = today_bookings
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

# === РЕГИСТРАЦИЯ МОДЕЛЕЙ ===

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'is_featured')
    list_filter = ('category', 'is_featured')
    search_fields = ('name', 'description')

# === ✅ ИСПРАВЛЕННЫЙ ADMIN ДЛЯ БРОНЕЙ ===
@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'get_table', 'date_time', 'status_badge', 'created_at')
    list_filter = ('status', 'date', 'table', 'guests')
    search_fields = ('name', 'phone')
    date_hierarchy = 'date'
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    list_per_page = 25

    fieldsets = (
        ('👤 Контактные данные', {'fields': ('name', 'phone', 'guests')}),
        ('📅 Бронирование', {'fields': ('table', 'date', 'time', 'status')}),
        ('🔒 Служебная информация', {'fields': ('created_at',), 'classes': ('collapse',)}),
    )

    actions = ['confirm_reservations', 'block_reservations', 'cancel_reservations']

    def get_table(self, obj):
        if obj.table:
            return f"Стол №{obj.table.number}"
        return "—"
    get_table.short_description = "Стол"

    def date_time(self, obj):
        # ✅ ИСПРАВЛЕНО: format_html с аргументами, а не f-строкой
        return format_html("<b>{}</b><br>{}", obj.date.strftime('%d.%m'), obj.time)
    date_time.short_description = "Дата / Время"

    def status_badge(self, obj):
        colors = {
            'pending': '#f59e0b',   # Жёлтый
            'confirmed': '#15803d', # Зелёный
            'blocked': '#ef4444',   # Красный
            'cancelled': '#6b7280'  # Серый
        }
        color = colors.get(obj.status, '#fff')
        # ✅ ИСПРАВЛЕНО: format_html с аргументами
        return format_html(
            '<span style="background:{}; color:#fff; padding:5px 12px; border-radius:20px; font-size:0.8rem; font-weight:600; white-space:nowrap;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = "Статус"

    # === МАССОВЫЕ ДЕЙСТВИЯ ===
    def confirm_reservations(self, request, queryset):
        updated = queryset.update(status='confirmed')
        self.message_user(request, f'✅ Успешно подтверждено: {updated} броней.')
    confirm_reservations.short_description = "Подтвердить выбранные"

    def block_reservations(self, request, queryset):
        updated = queryset.update(status='blocked')
        self.message_user(request, f'🚫 Успешно заблокировано: {updated} броней.')
    block_reservations.short_description = "Заблокировать выбранные"

    def cancel_reservations(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'❌ Успешно отменено: {updated} броней.')
    cancel_reservations.short_description = "Отменить выбранные"

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

@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ('number', 'seats', 'pos_x', 'pos_y', 'is_active')
    list_editable = ('pos_x', 'pos_y', 'is_active')

# === РЕГИСТРИРУЕМ ВСЕ МОДЕЛИ В КАСТОМНОМ САЙТЕ ===
admin_site.register(Category, CategoryAdmin)
admin_site.register(MenuItem, MenuItemAdmin)
admin_site.register(Reservation, ReservationAdmin)
admin_site.register(BarCategory, BarCategoryAdmin)
admin_site.register(BarItem, BarItemAdmin)
admin_site.register(KidsCategory, KidsCategoryAdmin)
admin_site.register(KidsItem, KidsItemAdmin)
admin_site.register(Table, TableAdmin)