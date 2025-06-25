from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Building, Floor, UnitType, Unit


@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    """إعدادات admin للمباني"""
    
    list_display = ('name', 'total_floors', 'has_mosque', 'has_elevator', 'has_parking', 'parking_spaces')
    list_filter = ('has_mosque', 'has_elevator', 'has_parking', 'created_at')
    search_fields = ('name', 'address', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (_('معلومات أساسية'), {
            'fields': ('name', 'address', 'description')
        }),
        (_('تفاصيل المبنى'), {
            'fields': ('total_floors', 'has_mosque', 'has_elevator', 'has_parking', 'parking_spaces')
        }),
        (_('معلومات النظام'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Floor)
class FloorAdmin(admin.ModelAdmin):
    """إعدادات admin للطوابق"""
    
    list_display = ('building', 'floor_number', 'name')
    list_filter = ('building', 'floor_number')
    search_fields = ('building__name', 'name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (_('معلومات الطابق'), {
            'fields': ('building', 'floor_number', 'name', 'description')
        }),
        (_('معلومات النظام'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(UnitType)
class UnitTypeAdmin(admin.ModelAdmin):
    """إعدادات admin لأنواع الوحدات"""
    
    list_display = ('name', 'description')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    """إعدادات admin للوحدات"""
    
    list_display = ('unit_number', 'floor', 'unit_type', 'area', 'rent_price', 'status')
    list_filter = ('status', 'unit_type', 'floor__building', 'has_balcony', 'has_kitchen')
    search_fields = ('unit_number', 'floor__building__name', 'floor__name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (_('معلومات أساسية'), {
            'fields': ('floor', 'unit_type', 'unit_number', 'status')
        }),
        (_('تفاصيل الوحدة'), {
            'fields': ('area', 'rent_price', 'description')
        }),
        (_('مميزات الوحدة'), {
            'fields': ('bedrooms', 'bathrooms', 'has_balcony', 'has_kitchen')
        }),
        (_('معلومات النظام'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """تحسين الاستعلامات"""
        return super().get_queryset(request).select_related('floor__building', 'unit_type')

