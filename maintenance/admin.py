from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import (
    MaintenanceRequest, MaintenancePhoto, MaintenanceProvider, 
    MaintenanceCategory, MaintenanceSchedule
)


class MaintenancePhotoInline(admin.TabularInline):
    """إدراج صور الصيانة في صفحة طلب الصيانة"""
    model = MaintenancePhoto
    extra = 1
    readonly_fields = ('uploaded_at',)


@admin.register(MaintenanceRequest)
class MaintenanceRequestAdmin(admin.ModelAdmin):
    """إعدادات admin لطلبات الصيانة"""
    
    list_display = ('request_number', 'title', 'unit', 'tenant', 'category', 'priority', 'status', 'scheduled_date', 'overdue_display')
    list_filter = ('category', 'priority', 'status', 'tenant_access_required', 'tenant_notified', 'created_at')
    search_fields = ('request_number', 'title', 'unit__unit_number', 'unit__floor__building__name', 'tenant__first_name', 'tenant__last_name')
    readonly_fields = ('created_at', 'updated_at', 'is_overdue')
    inlines = [MaintenancePhotoInline]
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (_('معلومات الطلب'), {
            'fields': ('request_number', 'unit', 'tenant', 'submitted_by', 'title', 'description')
        }),
        (_('تصنيف وأولوية'), {
            'fields': ('category', 'priority', 'status')
        }),
        (_('تفاصيل التنفيذ'), {
            'fields': ('assigned_to', 'scheduled_date', 'completed_date')
        }),
        (_('تكلفة'), {
            'fields': ('estimated_cost', 'actual_cost')
        }),
        (_('إعدادات الوصول'), {
            'fields': ('tenant_access_required', 'tenant_notified')
        }),
        (_('ملاحظات'), {
            'fields': ('notes',)
        }),
        (_('معلومات النظام'), {
            'fields': ('created_at', 'updated_at', 'is_overdue'),
            'classes': ('collapse',)
        }),
    )
    
    def overdue_display(self, obj):
        """عرض حالة التأخير مع تلوين"""
        if obj.is_overdue:
            return format_html('<span style="color: red;">متأخر</span>')
        elif obj.status == 'completed':
            return format_html('<span style="color: green;">مكتمل</span>')
        else:
            return format_html('<span style="color: blue;">في الموعد</span>')
    
    overdue_display.short_description = _('حالة التأخير')
    
    def get_queryset(self, request):
        """تحسين الاستعلامات"""
        return super().get_queryset(request).select_related('unit__floor__building', 'tenant', 'assigned_to')


@admin.register(MaintenancePhoto)
class MaintenancePhotoAdmin(admin.ModelAdmin):
    """إعدادات admin لصور الصيانة"""
    
    list_display = ('maintenance_request', 'photo_type', 'description', 'uploaded_by', 'uploaded_at')
    list_filter = ('photo_type', 'uploaded_at')
    search_fields = ('maintenance_request__request_number', 'description', 'uploaded_by__username')
    readonly_fields = ('uploaded_at',)
    
    fieldsets = (
        (_('معلومات الصورة'), {
            'fields': ('maintenance_request', 'photo', 'photo_type', 'description', 'uploaded_by')
        }),
        (_('معلومات النظام'), {
            'fields': ('uploaded_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(MaintenanceProvider)
class MaintenanceProviderAdmin(admin.ModelAdmin):
    """إعدادات admin لمقدمي خدمات الصيانة"""
    
    list_display = ('name', 'contact_person', 'phone_number', 'rating', 'is_active')
    list_filter = ('is_active', 'rating', 'specialties')
    search_fields = ('name', 'contact_person', 'phone_number', 'email')
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('specialties',)
    
    fieldsets = (
        (_('معلومات أساسية'), {
            'fields': ('name', 'contact_person', 'phone_number', 'email', 'address')
        }),
        (_('التخصصات والتقييم'), {
            'fields': ('specialties', 'rating', 'is_active')
        }),
        (_('ملاحظات'), {
            'fields': ('notes',)
        }),
        (_('معلومات النظام'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(MaintenanceCategory)
class MaintenanceCategoryAdmin(admin.ModelAdmin):
    """إعدادات admin لفئات الصيانة"""
    
    list_display = ('name', 'default_priority', 'estimated_duration_hours')
    list_filter = ('default_priority',)
    search_fields = ('name', 'description')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        (_('معلومات الفئة'), {
            'fields': ('name', 'description')
        }),
        (_('إعدادات افتراضية'), {
            'fields': ('default_priority', 'estimated_duration_hours')
        }),
        (_('معلومات النظام'), {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(MaintenanceSchedule)
class MaintenanceScheduleAdmin(admin.ModelAdmin):
    """إعدادات admin لجدولة الصيانة"""
    
    list_display = ('title', 'unit', 'category', 'frequency', 'next_due_date', 'is_active')
    list_filter = ('frequency', 'is_active', 'auto_create_requests', 'category')
    search_fields = ('title', 'unit__unit_number', 'unit__floor__building__name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'next_due_date'
    
    fieldsets = (
        (_('معلومات الجدولة'), {
            'fields': ('unit', 'category', 'title', 'description')
        }),
        (_('إعدادات التكرار'), {
            'fields': ('frequency', 'next_due_date')
        }),
        (_('إعدادات التشغيل'), {
            'fields': ('is_active', 'auto_create_requests')
        }),
        (_('معلومات النظام'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

