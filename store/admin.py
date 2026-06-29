from django.contrib import admin
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'name',
        'category',
        'price',
        'weight',
        'stock',
        'is_bestseller',
        'is_popular',
    ]

    list_filter = [
        'category',
        'is_bestseller',
        'is_popular',
        'is_bengali_sweets',
        'is_gift_box',
        'is_dry_sweets',
        'is_festival_special',

    ]

    search_fields = [
        'name',
        'description',
        'category__name'
    ]