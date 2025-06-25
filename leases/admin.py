from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import Lease, LeaseRenewal, LeaseTermination


@admin.register(Lease)
class LeaseAdmin(admin.ModelAdmin):
    """إعدادات admin لعقود الإيجار"""
    
    list_display = ('lease_number', 'tenant', 'unit', 'start_date', 'end_date', 'rent_amount', 'status', 'days_until_expiry_display')
    list_filter = ('status', 'payment_frequency', 'auto_renew', 'start_date', 'end_date')
    search_fields = ('lease_number', 'tenant__first_name', 'tenant__last_name', 'unit__unit_number', 'unit__floor__building__name')
    readonly_fields = ('created_at', 'updated_at', 'duration_months', 'is_active', 'is_expired', 'days_until_expiry', 'needs_renewal_notice')
    date_hierarchy = 'start_date'
    
    fieldsets = (
        (_('معلومات العقد'), {
            'fields': ('lease_number', 'unit', 'tenant', 'status')
        }),
        (_('تواريخ العقد'), {
            'fields': ('start_date', 'end_date')
        }),
        (_('تفاصيل مالية'), {
            'fields': ('rent_amount', 'deposit_amount', 'payment_frequency')
        }),
        (_('إعدادات التجديد'), {
            'fields': ('auto_renew', 'renewal_notice_days')
        }),
        (_('ملفات ومعلومات إضافية'), {
            'fields': ('contract_file', 'terms_and_conditions', 'notes')
        }),
        (_('معلومات النظام'), {
            'fields': ('created_at', 'updated_at', 'duration_months', 'is_active', 'is_expired', 'days_until_expiry', 'needs_renewal_notice'),
            'classes': ('collapse',)
        }),
    )
    
    def days_until_expiry_display(self, obj):
        """عرض الأيام المتبقية حتى انتهاء العقد مع تلوين"""
        days = obj.days_until_expiry
        if days is None:
            return '-'
        elif days < 0:
            return format_html('<span style="color: red;">منتهي منذ {} يوم</span>', abs(days))
        elif days <= 30:
            return format_html('<span style="color: orange;">{} يوم</span>', days)
        else:
            return format_html('<span style="color: green;">{} يوم</span>', days)
    
    days_until_expiry_display.short_description = _('الأيام المتبقية')
    
    def get_queryset(self, request):
        """تحسين الاستعلامات"""
        return super().get_queryset(request).select_related('tenant', 'unit__floor__building')


@admin.register(LeaseRenewal)
class LeaseRenewalAdmin(admin.ModelAdmin):
    """إعدادات admin لتجديدات العقود"""
    
    list_display = ('original_lease', 'new_lease', 'renewal_date', 'rent_increase_percentage')
    list_filter = ('renewal_date', 'rent_increase_percentage')
    search_fields = ('original_lease__lease_number', 'new_lease__lease_number')
    readonly_fields = ('created_at',)
    date_hierarchy = 'renewal_date'
    
    fieldsets = (
        (_('معلومات التجديد'), {
            'fields': ('original_lease', 'new_lease', 'renewal_date', 'rent_increase_percentage')
        }),
        (_('ملاحظات'), {
            'fields': ('notes',)
        }),
        (_('معلومات النظام'), {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(LeaseTermination)
class LeaseTerminationAdmin(admin.ModelAdmin):
    """إعدادات admin لإنهاءات العقود"""
    
    list_display = ('lease', 'termination_date', 'reason', 'penalty_amount', 'deposit_refund_amount')
    list_filter = ('reason', 'termination_date')
    search_fields = ('lease__lease_number', 'lease__tenant__first_name', 'lease__tenant__last_name')
    readonly_fields = ('created_at',)
    date_hierarchy = 'termination_date'
    
    fieldsets = (
        (_('معلومات الإنهاء'), {
            'fields': ('lease', 'termination_date', 'reason', 'notice_period_days')
        }),
        (_('تفاصيل مالية'), {
            'fields': ('penalty_amount', 'deposit_refund_amount')
        }),
        (_('ملاحظات'), {
            'fields': ('notes',)
        }),
        (_('معلومات النظام'), {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

