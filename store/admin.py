# store/admin.py

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import Category, Brand, Color, Condition, Size, Product, ProductImage, HeaderBanner


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    verbose_name = _('Изображение')
    verbose_name_plural = _('Изображения')
    readonly_fields = ['image_preview']

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 100px; object-fit: contain;" />',
                obj.image.url
            )
        return "-"

    image_preview.short_description = _('Превью')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'category',
        'brand',
        'price',
        'image_preview',
        'discount_info',
        'sku',
        'is_new_arrival'
    ]
    list_filter = ['category', 'brand', 'condition', 'gender', 'is_new_arrival']
    search_fields = ['name', 'sku', 'search_keywords']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline]
    readonly_fields = ['main_image_preview', 'discount_price']

    fieldsets = (
        (_('Основная информация'), {
            'fields': ('name', 'slug', 'category', 'brand', 'description', 'search_keywords')
        }),
        (_('Характеристики'), {
            'fields': ('gender', 'condition', 'colors', 'sizes')
        }),
        (_('Цены'), {
            'fields': ('price', 'discount_amount', 'discount_price')
        }),
        (_('Изображения'), {
            'fields': ('main_image_preview',)
        }),
        (_('Дополнительно'), {
            'fields': ('sku', 'is_new_arrival')
        }),
    )

    class Media:
        css = {
            'all': ('admin/css/taggit_styles.css',)
        }
        js = (
            'admin/js/taggit_script.js',
            'admin/js/jquery.init.js', # ДОБАВИЛ ЭТУ СТРОКУ
        )

    def image_preview(self, obj):
        first_image = obj.images.first()
        if first_image:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 50px; object-fit: contain;" />',
                first_image.image.url
            )
        return "-"

    image_preview.short_description = _('Фото')

    def discount_info(self, obj):
        if obj.discount_price:
            return format_html(
                '<span style="color: red;">{} (-{})</span>',
                obj.discount_price,
                obj.discount_amount
            )
        return "-"

    discount_info.short_description = _('Цена со скидкой')

    def main_image_preview(self, obj):
        first_image = obj.images.first()
        if first_image:
            return format_html(
                '<img src="{}" style="max-height: 200px; max-width: 200px; object-fit: contain;" />',
                first_image.image.url
            )
        return _("Нет изображения")

    main_image_preview.short_description = _('Главное изображение')


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ['name', 'color_preview', 'hex_code']
    search_fields = ['name']
    readonly_fields = ['color_preview']

    def color_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 50px; border: 1px solid #ddd; border-radius: 4px;" />',
                obj.image.url
            )
        elif obj.hex_code:
            return format_html(
                '<div style="width: 50px; height: 50px; background-color: {}; border: 1px solid #ddd; border-radius: 4px;"></div>',
                obj.hex_code
            )
        return "-"

    color_preview.short_description = _('Превью цвета')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(Condition)
class ConditionAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(HeaderBanner)
class HeaderBannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'show_on_homepage')
    list_filter = ('is_active', 'show_on_homepage')