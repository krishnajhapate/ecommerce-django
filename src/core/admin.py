from django.contrib import admin
from .models import OrderItem,Order,Item,Address,Payment,Coupon

def make_refund_requested(modeladmin,request,queryset):
    queryset.update(refund_requested=False,refund_granted=True)

make_refund_requested.short_description = "Update orders to refund granted"   

class OrderAdmin(admin.ModelAdmin):
    list_display=['user','ordered',
    'being_delivered',
    'recieved',
    'refund_requested',
    'refund_granted',
    'shipping_address',
    'billing_address',
    'payment',
    'coupon'
    ]
    list_display_links=[
        'user',
        'shipping_address',
        'billing_address',
        'payment',
        'coupon'
    ]
    list_filter=[
        'being_delivered',
        'recieved',
        'refund_requested',
        'refund_granted'
    ]
    search_fields=[
        'user__username',
        'ref_code'
    ]
    actions=[make_refund_requested]

class AddressModel(admin.ModelAdmin):
    list_display=[
        "user",
        "street_address",
        "apartment_address",
        "countries",
        "zip",
        "address_type"
    ]
    filter=[
        'default',
        'address_type',
        'country',
    ]
    search_fields=[
        'country',
        'user',
        "street_address",
        "apartment_address",
        "countries",
        "zip",
    ]

# Register your models here.
admin.site.register(OrderItem)
admin.site.register(Item)
admin.site.register(Order,OrderAdmin)
admin.site.register(Address,AddressModel)
admin.site.register(Payment)
admin.site.register(Coupon)