from django.contrib import admin
from .models import Category, Product, Order, OrderItem, Coupon


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


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ['product_name', 'price', 'quantity', 'subtotal']
    extra = 0
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer_name', 'status', 'is_paid', 'total_price', 'payment_method', 'created_at']
    list_filter = ['status', 'is_paid', 'payment_method', 'created_at']
    list_editable = ['status', 'is_paid']
    search_fields = ['customer_name', 'email', 'phone', 'id']
    date_hierarchy = 'created_at'
    readonly_fields = ['user', 'customer_name', 'email', 'phone', 'delivery_address', 'total_price', 'created_at', 'updated_at']
    inlines = [OrderItemInline]

    fieldsets = (
        ('Order Status', {'fields': ('status', 'is_paid')}),
        ('Customer', {'fields': ('customer_name', 'email', 'phone')}),
        ('Delivery', {'fields': ('delivery_address',)}),
        ('Special Instructions', {'fields': ('order_note',)}),
        ('Payment', {'fields': ('payment_method', 'total_price')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )

admin.site.register(Coupon)