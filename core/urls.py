from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('menu/', views.menu, name='menu'),
    path('bar/', views.bar_menu, name='bar_menu'),
    path('kids/', views.kids_menu, name='kids_menu'),
    
    # === НОВЫЕ МАРШРУТЫ ===
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    
    path('reservation/', views.reservation, name='reservation'),
    path('loyalty/', views.loyalty, name='loyalty'),
    
    path('receipt/<int:reservation_id>/', views.download_receipt, name='receipt'),
    
    path('hall/', views.hall_view, name='hall'),
    path('api/tables/', views.api_tables, name='api_tables'),
    path('api/tables-status/', views.api_tables_status, name='api_tables_status'),
    path('api/slots/', views.api_slots, name='api_slots'),
    
    path('init-hall/', views.init_hall_tables, name='init_hall'),
]