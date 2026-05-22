from django.db import models

# 1. Модель категорий (Паста, Пицца и т.д.)
class Category(models.Model):
    name = models.CharField('Название', max_length=100)
    slug = models.SlugField('URL-метка', unique=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name

# 2. Модель блюд (Меню)
class MenuItem(models.Model):
    category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE, 
        verbose_name='Категория',
        related_name='items'
    )
    name = models.CharField('Название блюда', max_length=200)
    description = models.TextField('Описание', blank=True)
    price = models.DecimalField('Цена (₽)', max_digits=8, decimal_places=2)
    image = models.ImageField('Фото', upload_to='dishes/', null=True, blank=True)
    is_featured = models.BooleanField('Рекомендуемое', default=False)

    class Meta:
        verbose_name = 'Блюдо'
        verbose_name_plural = 'Блюда'
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.name} ({self.price} ₽)"

# 3. Модель бронирования столов
class Reservation(models.Model):
    name = models.CharField('Ваше имя', max_length=100)
    phone = models.CharField('Телефон', max_length=20)
    date = models.DateField('Дата бронирования')
    time = models.TimeField('Время')
    guests = models.PositiveIntegerField('Количество гостей', default=2)
    created_at = models.DateTimeField('Создано', auto_now_add=True)

    class Meta:
        verbose_name = 'Бронь'
        verbose_name_plural = 'Бронирования'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} | {self.date} {self.time}"
    
    # === BAR MENU MODELS ===
class BarCategory(models.Model):
    name = models.CharField('Название категории', max_length=100)
    slug = models.SlugField('URL-метка', unique=True)
    order = models.PositiveIntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Категория бара'
        verbose_name_plural = 'Категории бара'
        ordering = ['order']

    def __str__(self):
        return self.name

class BarItem(models.Model):
    BAR_TYPES = [
        ('non_alcoholic', 'Б/А напитки'),
        ('alcoholic', 'Алкогольные напитки'),
        ('cocktail_classic', 'Коктейли классические'),
        ('cocktail_author', 'Коктейли авторские'),
    ]

    category = models.ForeignKey(
        BarCategory, 
        on_delete=models.CASCADE, 
        verbose_name='Категория',
        related_name='items'
    )
    bar_type = models.CharField(
        'Тип напитка',
        max_length=20,
        choices=BAR_TYPES,
        default='non_alcoholic'
    )
    name = models.CharField('Название', max_length=200)
    description = models.TextField('Описание', blank=True)
    volume = models.CharField('Объём (мл)', max_length=50, blank=True)
    price = models.DecimalField('Цена (₽)', max_digits=8, decimal_places=2)
    image = models.ImageField('Фото', upload_to='bar/', null=True, blank=True)
    is_featured = models.BooleanField('Рекомендуемое', default=False)
    alcohol_content = models.CharField('Крепость', max_length=50, blank=True)

    class Meta:
        verbose_name = 'Напиток'
        verbose_name_plural = 'Барное меню'
        ordering = ['category', 'bar_type', 'name']

    def __str__(self):
        return f"{self.name} ({self.price} ₽)"

# === KIDS MENU MODELS ===
class KidsCategory(models.Model):
    name = models.CharField('Название категории', max_length=100)
    slug = models.SlugField('URL-метка', unique=True)

    class Meta:
        verbose_name = 'Категория детского меню'
        verbose_name_plural = 'Категории детского меню'

    def __str__(self):
        return self.name

class KidsItem(models.Model):
    category = models.ForeignKey(
        KidsCategory, 
        on_delete=models.CASCADE, 
        verbose_name='Категория',
        related_name='items'
    )
    name = models.CharField('Название блюда', max_length=200)
    description = models.TextField('Описание', blank=True)
    price = models.DecimalField('Цена (₽)', max_digits=6, decimal_places=2)
    image = models.ImageField('Фото', upload_to='kids/', null=True, blank=True)
    age_recommendation = models.CharField('Рекомендуемый возраст', max_length=50, blank=True)
    is_popular = models.BooleanField('Популярное', default=False)

    class Meta:
        verbose_name = 'Блюдо детского меню'
        verbose_name_plural = 'Детское меню'
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.name} ({self.price} ₽)"