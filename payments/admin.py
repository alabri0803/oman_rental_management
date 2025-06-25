from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import Payment, PaymentSchedule, Receipt


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """إعدادات admin للدفعات"""
    
    list_display = ('lease', 'payment_type', 'amount', 'due_date', 'payment_date', 'status', 'overdue_display')
    list_filter = ('payment_type', 'payment_method', 'status', 'due_date', 'payment_date')
    search_fields = ('lease__lease_number', 'lease__tenant__first_name', 'lease__tenant__last_name', 'reference_number', 'receipt_number')
    readonly_fields = ('created_at', 'updated_at', 'total_amount', 'is_overdue', 'days_overdue')
    date_hierarchy = 'due_date'
    
    fieldsets = (
        (_('معلومات الدفعة'), {
            'fields': ('lease', 'payment_type', 'amount', 'due_date', 'status')
        }),
        (_('تفاصيل الدفع'), {
            'fields': ('payment_date', 'payment_method', 'reference_number', 'receipt_number')
        }),
        (_('رسوم وخصومات'), {
            'fields': ('late_fee', 'discount')
        }),
        (_('ملاحظات'), {
            'fields': ('notes',)
        }),
        (_('معلومات النظام'), {
            'fields': ('created_at', 'updated_at', 'total_amount', 'is_overdue', 'days_overdue'),
            'classes': ('collapse',)
        }),
    )
    
    def overdue_display(self, obj):
        """عرض حالة التأخير مع تلوين"""
        if obj.is_overdue:
            return format_html('<span style="color: red;">متأخر {} يوم</span>', obj.days_overdue)
        elif obj.status == 'paid':
            return format_html('<span style="color: green;">مدفوع</span>')
        else:
            return format_html('<span style="color: blue;">في الموعد</span>')
    
    overdue_display.short_description = _('حالة التأخير')
    
    def get_queryset(self, request):
        """تحسين الاستعلامات"""
        return super().get_queryset(request).select_related('lease__tenant', 'lease__unit')


@admin.register(PaymentSchedule)
class PaymentScheduleAdmin(admin.ModelAdmin):
    """إعدادات admin لجدولة الدفعات"""
    
    list_display = ('schedule_name', 'lease', 'start_date', 'end_date', 'payment_amount', 'frequency_days', 'is_active')
    list_filter = ('is_active', 'auto_generate', 'start_date', 'end_date')
    search_fields = ('schedule_name', 'lease__lease_number', 'lease__tenant__first_name', 'lease__tenant__last_name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (_('معلومات الجدولة'), {
            'fields': ('lease', 'schedule_name', 'start_date', 'end_date')
        }),
        (_('تفاصيل الدفع'), {
            'fields': ('payment_amount', 'frequency_days')
        }),
        (_('إعدادات'), {
            'fields': ('is_active', 'auto_generate')
        }),
        (_('معلومات النظام'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['generate_payments_for_selected']
    
    def generate_payments_for_selected(self, request, queryset):
        """إنشاء دفعات للجدولات المحددة"""
        total_generated = 0
        for schedule in queryset:
            if schedule.is_active:
                generated = schedule.generate_payments()
                if generated:
                    total_generated += generated
        
        self.message_user(request, f'تم إنشاء {total_generated} دفعة جديدة.')
    
    generate_payments_for_selected.short_description = _('إنشاء دفعات للجدولات المحددة')


@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    """إعدادات admin للإيصالات"""
    
    list_display = ('receipt_number', 'payment', 'issued_date', 'issued_by')
    list_filter = ('issued_date',)
    search_fields = ('receipt_number', 'payment__lease__tenant__first_name', 'payment__lease__tenant__last_name', 'issued_by')
    readonly_fields = ('created_at',)
    date_hierarchy = 'issued_date'
    
    fieldsets = (
        (_('معلومات الإيصال'), {
            'fields': ('payment', 'receipt_number', 'issued_date', 'issued_by')
        }),
        (_('ملاحظات'), {
            'fields': ('notes',)
        }),
        (_('معلومات النظام'), {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

