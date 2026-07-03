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
    ]

    search_fields = [
        'name',
        'description',
        'category__name',
    ]