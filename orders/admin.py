from django.contrib import admin
from .models import *

# Register your models here.
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number','full_name','phone','email','city','order_toal','tax','status','is_ordered']
    list_filter = ['status','is_ordered']
    search_fields = ['order_number','first_name','last_name']
    list_per_page = 20

admin.site.register(Payment)
admin.site.register(Order)
admin.site.register(OrderProduct)
