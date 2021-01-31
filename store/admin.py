from django.contrib import admin
from .models import *


class CustomerAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'email',
        'name',
        'phone_number',
    ]
    search_fields = [
        'user__username',
        'email',
        'name',
        'phone_number',
    ]


admin.site.register(Customer, CustomerAdmin)


class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title', 'category', 'price')}
    list_display = [
        'title',
        'price',
        'discount_price',
        'category',
    ]
    search_fields = [
        'title',
        'price',
        'discount_price',
        'category',
    ]


admin.site.register(Product, ProductAdmin)


class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'customer',
        'ordered_date',
        'order_complete',
        'shipping_address',
        'status',
        'refund_requested',
        'refund_granted',
    ]


admin.site.register(Order, OrderAdmin)


class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = [
        'country',
        'customer',
        'state_province',
        'city',
        'zip',
    ]


admin.site.register(ShippingAddress, ShippingAddressAdmin)

admin.site.register(OrderItem)
admin.site.register(Payment)
admin.site.register(Coupon)
admin.site.register(Refund)
