from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """إعدادات admin للمستخدم المخصص"""
    
    fieldsets = UserAdmin.fieldsets + (
        (_('معلومات إضافية'), {
            'fields': ('phone_number', 'nationality', 'national_id', 'address')
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        (_('معلومات إضافية'), {
            'fields': ('phone_number', 'nationality', 'national_id', 'address')
        }),
    )
    
    list_display = ('username', 'email', 'first_name', 'last_name', 'phone_number', 'is_staff')
    list_filter = UserAdmin.list_filter + ('nationality',)
    search_fields = ('username', 'first_name', 'last_name', 'email', 'phone_number', 'national_id')

