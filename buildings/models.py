from django.db import models
from django.utils.translation import gettext_lazy as _


class Building(models.Model):
    """
    نموذج المبنى
    """
    name = models.CharField(
        _('اسم المبنى'),
        max_length=200,
        help_text=_('اسم المبنى التجاري')
    )
    
    address = models.TextField(
        _('العنوان'),
        help_text=_('العنوان الكامل للمبنى')
    )
    
    description = models.TextField(
        _('الوصف'),
        blank=True,
        null=True,
        help_text=_('وصف تفصيلي للمبنى وخدماته')
    )
    
    total_floors = models.PositiveIntegerField(
        _('إجمالي الطوابق'),
        default=1,
        help_text=_('العدد الإجمالي للطوابق في المبنى')
    )
    
    has_mosque = models.BooleanField(
        _('يحتوي على مصلى'),
        default=False,
        help_text=_('هل يحتوي المبنى على مصلى؟')
    )
    
    has_elevator = models.BooleanField(
        _('يحتوي على مصعد'),
        default=False,
        help_text=_('هل يحتوي المبنى على مصعد؟')
    )
    
    has_parking = models.BooleanField(
        _('يحتوي على مواقف'),
        default=False,
        help_text=_('هل يحتوي المبنى على مواقف سيارات؟')
    )
    
    parking_spaces = models.PositiveIntegerField(
        _('عدد مواقف السيارات'),
        default=0,
        help_text=_('عدد مواقف السيارات المتاحة')
    )
    
    created_at = models.DateTimeField(
        _('تاريخ الإنشاء'),
        auto_now_add=True
    )
    
    updated_at = models.DateTimeField(
        _('تاريخ التحديث'),
        auto_now=True
    )

    class Meta:
        verbose_name = _('مبنى')
        verbose_name_plural = _('المباني')
        ordering = ['name']
        
    def __str__(self):
        return self.name


class Floor(models.Model):
    """
    نموذج الطابق
    """
    building = models.ForeignKey(
        Building,
        on_delete=models.CASCADE,
        related_name='floors',
        verbose_name=_('المبنى'),
        help_text=_('المبنى الذي ينتمي إليه الطابق')
    )
    
    floor_number = models.IntegerField(
        _('رقم الطابق'),
        help_text=_('رقم الطابق (0 للطابق الأرضي، 1 للطابق الأول، إلخ)')
    )
    
    name = models.CharField(
        _('اسم الطابق'),
        max_length=100,
        help_text=_('اسم الطابق (مثل: الطابق الأرضي، الطابق الأول)')
    )
    
    description = models.TextField(
        _('الوصف'),
        blank=True,
        null=True,
        help_text=_('وصف إضافي للطابق')
    )
    
    created_at = models.DateTimeField(
        _('تاريخ الإنشاء'),
        auto_now_add=True
    )
    
    updated_at = models.DateTimeField(
        _('تاريخ التحديث'),
        auto_now=True
    )

    class Meta:
        verbose_name = _('طابق')
        verbose_name_plural = _('الطوابق')
        ordering = ['building', 'floor_number']
        unique_together = ['building', 'floor_number']
        
    def __str__(self):
        return f"{self.building.name} - {self.name}"


class UnitType(models.Model):
    """
    نموذج نوع الوحدة
    """
    name = models.CharField(
        _('اسم نوع الوحدة'),
        max_length=100,
        unique=True,
        help_text=_('نوع الوحدة (مثل: شقة، مكتب، محل تجاري)')
    )
    
    description = models.TextField(
        _('الوصف'),
        blank=True,
        null=True,
        help_text=_('وصف نوع الوحدة')
    )
    
    created_at = models.DateTimeField(
        _('تاريخ الإنشاء'),
        auto_now_add=True
    )
    
    updated_at = models.DateTimeField(
        _('تاريخ التحديث'),
        auto_now=True
    )

    class Meta:
        verbose_name = _('نوع الوحدة')
        verbose_name_plural = _('أنواع الوحدات')
        ordering = ['name']
        
    def __str__(self):
        return self.name


class Unit(models.Model):
    """
    نموذج الوحدة (شقة/مكتب/محل)
    """
    STATUS_CHOICES = [
        ('vacant', _('شاغرة')),
        ('rented', _('مؤجرة')),
        ('maintenance', _('تحت الصيانة')),
        ('reserved', _('محجوزة')),
    ]
    
    floor = models.ForeignKey(
        Floor,
        on_delete=models.CASCADE,
        related_name='units',
        verbose_name=_('الطابق'),
        help_text=_('الطابق الذي تقع فيه الوحدة')
    )
    
    unit_type = models.ForeignKey(
        UnitType,
        on_delete=models.CASCADE,
        related_name='units',
        verbose_name=_('نوع الوحدة'),
        help_text=_('نوع الوحدة')
    )
    
    unit_number = models.CharField(
        _('رقم الوحدة'),
        max_length=20,
        help_text=_('رقم الوحدة أو الشقة')
    )
    
    area = models.DecimalField(
        _('المساحة (متر مربع)'),
        max_digits=10,
        decimal_places=2,
        help_text=_('مساحة الوحدة بالمتر المربع')
    )
    
    rent_price = models.DecimalField(
        _('سعر الإيجار الشهري'),
        max_digits=10,
        decimal_places=3,
        help_text=_('سعر الإيجار الشهري بالريال العماني')
    )
    
    status = models.CharField(
        _('حالة الوحدة'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='vacant',
        help_text=_('الحالة الحالية للوحدة')
    )
    
    description = models.TextField(
        _('الوصف'),
        blank=True,
        null=True,
        help_text=_('وصف تفصيلي للوحدة ومميزاتها')
    )
    
    bedrooms = models.PositiveIntegerField(
        _('عدد غرف النوم'),
        default=0,
        help_text=_('عدد غرف النوم (للشقق السكنية)')
    )
    
    bathrooms = models.PositiveIntegerField(
        _('عدد دورات المياه'),
        default=1,
        help_text=_('عدد دورات المياه')
    )
    
    has_balcony = models.BooleanField(
        _('يحتوي على شرفة'),
        default=False,
        help_text=_('هل تحتوي الوحدة على شرفة؟')
    )
    
    has_kitchen = models.BooleanField(
        _('يحتوي على مطبخ'),
        default=True,
        help_text=_('هل تحتوي الوحدة على مطبخ؟')
    )
    
    created_at = models.DateTimeField(
        _('تاريخ الإنشاء'),
        auto_now_add=True
    )
    
    updated_at = models.DateTimeField(
        _('تاريخ التحديث'),
        auto_now=True
    )

    class Meta:
        verbose_name = _('وحدة')
        verbose_name_plural = _('الوحدات')
        ordering = ['floor__building', 'floor__floor_number', 'unit_number']
        unique_together = ['floor', 'unit_number']
        
    def __str__(self):
        return f"{self.floor.building.name} - {self.floor.name} - وحدة {self.unit_number}"
    
    @property
    def building(self):
        """إرجاع المبنى الذي تنتمي إليه الوحدة"""
        return self.floor.building
    
    @property
    def is_available(self):
        """فحص ما إذا كانت الوحدة متاحة للإيجار"""
        return self.status == 'vacant'

