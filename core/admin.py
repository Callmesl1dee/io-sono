from django.contrib import admin
from .models import Category, MenuItem, Reservation

# Регистрация Категорий
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}  # Автоматически заполняет URL-метку

# Регистрация Блюд (Меню)
@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'is_featured')  # Столбцы в списке
    list_filter = ('category', 'is_featured')                    # Фильтры справа
    search_fields = ('name', 'description')                      # Поле поиска
    list_editable = ('price', 'is_featured')                     # Можно менять прямо в списке

# Регистрация Бронирований
@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'date', 'time', 'guests', 'created_at')
    list_filter = ('date', 'guests')
    readonly_fields = ('created_at',)                            # Поле только для чтения