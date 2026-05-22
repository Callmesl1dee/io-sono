from django.contrib import admin
from .models import Category, MenuItem, Reservation, BarCategory, BarItem, KidsCategory, KidsItem

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
    list_display = ('name', 'phone', 'date', 'time', 'guests', 'created_at')
    list_filter = ('date', 'guests')
    readonly_fields = ('created_at',)

# Bar Admin
@admin.register(BarCategory)
class BarCategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ('name', 'order')

@admin.register(BarItem)
class BarItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'bar_type', 'price', 'is_featured')
    list_filter = ('bar_type', 'category', 'is_featured')
    search_fields = ('name', 'description')

# Kids Menu Admin
@admin.register(KidsCategory)
class KidsCategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}

@admin.register(KidsItem)
class KidsItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'is_popular')
    list_filter = ('category', 'is_popular')
    search_fields = ('name', 'description')