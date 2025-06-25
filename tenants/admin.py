from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Tenant, TenantDocument


class TenantDocumentInline(admin.TabularInline):
    """إدراج وثائق المستأجر في صفحة المستأجر"""
    model = TenantDocument
    extra = 1
    readonly_fields = ('uploaded_at',)


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    """إعدادات admin للمستأجرين"""
    
    list_display = ('full_name', 'national_id', 'phone_number', 'email', 'nationality', 'is_active')
    list_filter = ('gender', 'marital_status', 'nationality', 'is_active', 'created_at')
    search_fields = ('first_name', 'last_name', 'national_id', 'phone_number', 'email')
    readonly_fields = ('created_at', 'updated_at', 'age')
    inlines = [TenantDocumentInline]
    
    fieldsets = (
        (_('معلومات شخصية'), {
            'fields': ('first_name', 'last_name', 'national_id', 'date_of_birth', 'gender', 'marital_status')
        }),
        (_('معلومات الاتصال'), {
            'fields': ('phone_number', 'email', 'address')
        }),
        (_('معلومات إضافية'), {
            'fields': ('nationality', 'occupation', 'employer', 'monthly_income')
        }),
        (_('جهة الاتصال في حالات الطوارئ'), {
            'fields': ('emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relationship')
        }),
        (_('ملاحظات وحالة'), {
            'fields': ('notes', 'is_active')
        }),
        (_('ربط بالنظام'), {
            'fields': ('user',),
            'classes': ('collapse',)
        }),
        (_('معلومات النظام'), {
            'fields': ('created_at', 'updated_at', 'age'),
            'classes': ('collapse',)
        }),
    )
    
    def full_name(self, obj):
        """عرض الاسم الكامل"""
        return obj.full_name
    full_name.short_description = _('الاسم الكامل')


@admin.register(TenantDocument)
class TenantDocumentAdmin(admin.ModelAdmin):
    """إعدادات admin لوثائق المستأجرين"""
    
    list_display = ('tenant', 'document_type', 'title', 'uploaded_at')
    list_filter = ('document_type', 'uploaded_at')
    search_fields = ('tenant__first_name', 'tenant__last_name', 'title', 'description')
    readonly_fields = ('uploaded_at',)
    
    fieldsets = (
        (_('معلومات الوثيقة'), {
            'fields': ('tenant', 'document_type', 'title', 'file', 'description')
        }),
        (_('معلومات النظام'), {
            'fields': ('uploaded_at',),
            'classes': ('collapse',)
        }),
    )

