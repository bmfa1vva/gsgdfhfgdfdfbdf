# store/models.py

from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

class Category(models.Model):
    name = models.CharField(_('Название'), max_length=100, unique=True)
    slug = models.SlugField(_('SLUG'), max_length=100, unique=True, blank=True)

    class Meta:
        verbose_name = _('Категория')
        verbose_name_plural = _('Категории')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Brand(models.Model):
    name = models.CharField(_('Название'), max_length=100, unique=True)

    class Meta:
        verbose_name = _('Бренд')
        verbose_name_plural = _('Бренды')

    def __str__(self):
        return self.name

class Color(models.Model):
    name = models.CharField(_('Название'), max_length=50)
    hex_code = models.CharField(_('HEX-код'), max_length=7, blank=True)
    image = models.ImageField(_('Изображение'), upload_to='colors/', blank=True, null=True)

    class Meta:
        verbose_name = _('Цвет')
        verbose_name_plural = _('Цвета')

    def __str__(self):
        return self.name

class Condition(models.Model):
    name = models.CharField(_('Состояние'), max_length=50)

    class Meta:
        verbose_name = _('Состояние')
        verbose_name_plural = _('Состояния')

    def __str__(self):
        return self.name

class Size(models.Model):
    name = models.CharField(_('Размер'), max_length=20)

    class Meta:
        verbose_name = _('Размер')
        verbose_name_plural = _('Размеры')

    def __str__(self):
        return self.name

class Product(models.Model):
    GENDER_CHOICES = [
        ('M', _('Мужской')),
        ('F', _('Женский')),
        ('U', _('Унисекс')),
    ]

    name = models.CharField(_('Название'), max_length=200)
    slug = models.SlugField(_('SLUG'), max_length=200, unique=True, blank=True)
    category = models.ForeignKey(
        Category,
        verbose_name=_('Категория'),
        on_delete=models.CASCADE,
        related_name='products'
    )
    brand = models.ForeignKey(
        Brand,
        verbose_name=_('Бренд'),
        on_delete=models.CASCADE
    )
    colors = models.ManyToManyField(
        Color,
        verbose_name=_('Цвета')
    )
    condition = models.ForeignKey(
        Condition,
        verbose_name=_('Состояние'),
        on_delete=models.CASCADE
    )
    sizes = models.ManyToManyField(
        Size,
        verbose_name=_('Размеры')
    )
    gender = models.CharField(
        _('Пол'),
        max_length=1,
        choices=GENDER_CHOICES
    )
    price = models.DecimalField(
        _('Цена'),
        max_digits=10,
        decimal_places=2
    )
    discount_amount = models.DecimalField(
        _('Сумма скидки'),
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )
    discount_price = models.DecimalField(
        _('Цена со скидкой'),
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )
    sku = models.CharField(
        _('Артикул'),
        max_length=50,
        unique=True
    )
    description = models.TextField(
        _('Описание'),
        blank=True
    )
    # --- НОВОЕ ПОЛЕ: Ключевые слова для поиска ---
    search_keywords = models.CharField(
        _('Ключевые слова для поиска'),
        max_length=500,
        blank=True,
        help_text=_("Скрытые ключевые слова для поиска (например, 'кроссовки адидас', 'джинсы синие')")
    )
    # --- КОНЕЦ НОВОГО ПОЛЯ ---
    created_at = models.DateTimeField(
        _('Дата создания'),
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        _('Дата обновления'),
        auto_now=True
    )
    is_new_arrival = models.BooleanField(
        _('Новинка'),
        default=False
    )

    class Meta:
        verbose_name = _('Товар')
        verbose_name_plural = _('Товары')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        if self.discount_amount and self.price:
            self.discount_price = self.price - self.discount_amount
        else:
            self.discount_price = None
        super().save(*args, **kwargs)

class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        verbose_name=_('Товар'),
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(
        _('Изображение'),
        upload_to='products/'
    )

    class Meta:
        verbose_name = _('Изображение товара')
        verbose_name_plural = _('Изображения товаров')

    def __str__(self):
        return f"{_('Изображение для')} {self.product.name}"



class HeaderBanner(models.Model):
    title = models.CharField(_('Заголовок'), max_length=200, blank=True)
    image = models.ImageField(_('Изображение'), upload_to='banners/')
    url = models.URLField(_('Ссылка'), blank=True, help_text="Куда ведёт баннер (оставьте пустым, если не нужно).")
    is_active = models.BooleanField(_('Активен'), default=True)
    show_on_homepage = models.BooleanField(_('Показать только на главной странице'), default=False)

    class Meta:
        verbose_name = _('Баннер под шапкой')
        verbose_name_plural = _('Баннеры под шапкой')

    def __str__(self):
        return self.title if self.title else "Баннер без названия"