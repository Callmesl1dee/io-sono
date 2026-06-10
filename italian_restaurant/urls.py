from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core import views
from core.admin import admin_site  # ← Импортируем наш кастомный admin_site

urlpatterns = [
    # Аналитика (ДО админки)
    path('dashboard/', views.admin_analytics, name='admin_analytics'),
    
    # Кастомная админка ← ВАЖНО: admin_site.urls, а не admin.site.urls
    path('admin/', admin_site.urls),
    
    # Основной сайт
    path('', include('core.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    
    