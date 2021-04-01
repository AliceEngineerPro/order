from django.contrib import admin

# Register your models here.

from .models import WxUsers, Order


@admin.register(WxUsers)
class WxUsersAdmin(admin.ModelAdmin):
    list_display = ('wx_id', 'open_id', 'nickname', 'name', 'department', 'created_at', 'updated_at')
    search_fields = list_display
    list_filter = list_display


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", 'appointment_at', 'meal_type', 'wx_id', 'is_delete', 'created_at', 'updated_at')
    search_fields = list_display
    list_filter = list_display
