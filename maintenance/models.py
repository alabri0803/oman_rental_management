from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from buildings.models import Unit
from tenants.models import Tenant
from core.models import User


class MaintenanceRequest(models.Model):
    """
    نموذج طلب الصيانة
    """
    PRIORITY_CHOICES = [
        ('low', _('منخفضة')),
        ('medium', _('متوسطة')),
        ('high', _('عالية')),
        ('urgent', _('عاجلة')),
    ]
    
    STATUS_CHOICES = [
        ('submitted', _('مقدم')),
        ('acknowledged', _('مستلم')),
        ('in_progress', _('قيد التنفيذ')),
        ('completed', _('مكتمل')),
        ('cancelled', _('ملغى')),
        ('on_hold', _('معلق')),
    ]
    
    CATEGORY_CHOICES = [
        ('plumbing', _('سباكة')),
        ('electrical', _('كهرباء')),
        ('hvac', _('تكييف وتهوية')),
        ('appliances', _('أجهزة')),
        ('structural', _('إنشائية')),
        ('painting', _('دهان')),
        ('flooring', _('أرضيات')),
        ('doors_windows', _('أبواب ونوافذ')),
        ('cleaning', _('تنظيف')),
        ('pest_control', _('مكافحة حشرات')),
        ('security', _('أمن')),
        ('other', _('أخرى')),
    ]
    
    unit = models.ForeignKey(
        Unit,
        on_delete=models.CASCADE,
        related_name='maintenance_requests',
        verbose_name=_('الوحدة'),
        help_text=_('الوحدة التي تحتاج صيانة')
    )
    
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='maintenance_requests',
        verbose_name=_('المستأجر'),
        blank=True,
        null=True,
        help_text=_('المستأجر الذي قدم الطلب (إذا كان من المستأجر)')
    )
    
    submitted_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='submitted_maintenance_requests',
        verbose_name=_('مقدم الطلب'),
        help_text=_('المستخدم الذي قدم طلب الصيانة')
    )
    
    request_number = models.CharField(
        _('رقم الطلب'),
        max_length=50,
        unique=True,
        help_text=_('رقم طلب الصيانة الفريد')
    )
    
    title = models.CharField(
        _('عنوان الطلب'),
        max_length=200,
        help_text=_('عنوان مختصر لطلب الصيانة')
    )
    
    description = models.TextField(
        _('وصف المشكلة'),
        help_text=_('وصف تفصيلي للمشكلة أو الصيانة المطلوبة')
    )
    
    category = models.CharField(
        _('فئة الصيانة'),
        max_length=20,
        choices=CATEGORY_CHOICES,
        help_text=_('فئة نوع الصيانة المطلوبة')
    )
    
    priority = models.CharField(
        _('الأولوية'),
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium',
        help_text=_('أولوية طلب الصيانة')
    )
    
    status = models.CharField(
        _('حالة الطلب'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='submitted',
        help_text=_('الحالة الحالية لطلب الصيانة')
    )
    
    estimated_cost = models.DecimalField(
        _('التكلفة المقدرة'),
        max_digits=10,
        decimal_places=3,
        blank=True,
        null=True,
        help_text=_('التكلفة المقدرة للصيانة بالريال العماني')
    )
    
    actual_cost = models.DecimalField(
        _('التكلفة الفعلية'),
        max_digits=10,
        decimal_places=3,
        blank=True,
        null=True,
        help_text=_('التكلفة الفعلية للصيانة بالريال العماني')
    )
    
    scheduled_date = models.DateTimeField(
        _('تاريخ الموعد المحدد'),
        blank=True,
        null=True,
        help_text=_('تاريخ ووقت الموعد المحدد للصيانة')
    )
    
    completed_date = models.DateTimeField(
        _('تاريخ الإكمال'),
        blank=True,
        null=True,
        help_text=_('تاريخ ووقت إكمال الصيانة')
    )
    
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='assigned_maintenance_requests',
        verbose_name=_('مكلف بالصيانة'),
        blank=True,
        null=True,
        help_text=_('الشخص المكلف بتنفيذ الصيانة')
    )
    
    tenant_access_required = models.BooleanField(
        _('يتطلب دخول المستأجر'),
        default=True,
        help_text=_('هل تتطلب الصيانة دخول الوحدة؟')
    )
    
    tenant_notified = models.BooleanField(
        _('تم إشعار المستأجر'),
        default=False,
        help_text=_('هل تم إشعار المستأجر بالموعد؟')
    )
    
    notes = models.TextField(
        _('ملاحظات'),
        blank=True,
        null=True,
        help_text=_('ملاحظات إضافية حول طلب الصيانة')
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
        verbose_name = _('طلب صيانة')
        verbose_name_plural = _('طلبات الصيانة')
        ordering = ['-created_at']
        
    def __str__(self):
        return f"طلب {self.request_number} - {self.title} - {self.unit}"
    
    @property
    def is_overdue(self):
        """فحص ما إذا كان الطلب متأخر عن الموعد المحدد"""
        if self.scheduled_date and self.status not in ['completed', 'cancelled']:
            from django.utils import timezone
            return timezone.now() > self.scheduled_date
        return False


class MaintenancePhoto(models.Model):
    """
    نموذج صور الصيانة
    """
    PHOTO_TYPES = [
        ('before', _('قبل الصيانة')),
        ('during', _('أثناء الصيانة')),
        ('after', _('بعد الصيانة')),
        ('damage', _('ضرر')),
        ('parts', _('قطع غيار')),
    ]
    
    maintenance_request = models.ForeignKey(
        MaintenanceRequest,
        on_delete=models.CASCADE,
        related_name='photos',
        verbose_name=_('طلب الصيانة'),
        help_text=_('طلب الصيانة المرتبط بالصورة')
    )
    
    photo = models.ImageField(
        _('الصورة'),
        upload_to='maintenance_photos/',
        help_text=_('صورة متعلقة بطلب الصيانة')
    )
    
    photo_type = models.CharField(
        _('نوع الصورة'),
        max_length=20,
        choices=PHOTO_TYPES,
        help_text=_('نوع الصورة')
    )
    
    description = models.CharField(
        _('وصف الصورة'),
        max_length=200,
        blank=True,
        null=True,
        help_text=_('وصف مختصر للصورة')
    )
    
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='uploaded_maintenance_photos',
        verbose_name=_('رفع بواسطة'),
        help_text=_('المستخدم الذي رفع الصورة')
    )
    
    uploaded_at = models.DateTimeField(
        _('تاريخ الرفع'),
        auto_now_add=True
    )

    class Meta:
        verbose_name = _('صورة صيانة')
        verbose_name_plural = _('صور الصيانة')
        ordering = ['-uploaded_at']
        
    def __str__(self):
        return f"صورة {self.get_photo_type_display()} - {self.maintenance_request.request_number}"


class MaintenanceProvider(models.Model):
    """
    نموذج مقدم خدمة الصيانة
    """
    name = models.CharField(
        _('اسم مقدم الخدمة'),
        max_length=200,
        help_text=_('اسم الشركة أو الشخص مقدم خدمة الصيانة')
    )
    
    contact_person = models.CharField(
        _('الشخص المسؤول'),
        max_length=200,
        help_text=_('اسم الشخص المسؤول للتواصل')
    )
    
    phone_number = models.CharField(
        _('رقم الهاتف'),
        max_length=17,
        help_text=_('رقم هاتف مقدم الخدمة')
    )
    
    email = models.EmailField(
        _('البريد الإلكتروني'),
        blank=True,
        null=True,
        help_text=_('البريد الإلكتروني لمقدم الخدمة')
    )
    
    address = models.TextField(
        _('العنوان'),
        help_text=_('عنوان مقدم الخدمة')
    )
    
    specialties = models.ManyToManyField(
        'MaintenanceCategory',
        related_name='providers',
        verbose_name=_('التخصصات'),
        help_text=_('تخصصات مقدم الخدمة')
    )
    
    rating = models.DecimalField(
        _('التقييم'),
        max_digits=3,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        default=0,
        help_text=_('تقييم مقدم الخدمة من 0 إلى 5')
    )
    
    is_active = models.BooleanField(
        _('نشط'),
        default=True,
        help_text=_('هل مقدم الخدمة نشط؟')
    )
    
    notes = models.TextField(
        _('ملاحظات'),
        blank=True,
        null=True,
        help_text=_('ملاحظات حول مقدم الخدمة')
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
        verbose_name = _('مقدم خدمة صيانة')
        verbose_name_plural = _('مقدمو خدمات الصيانة')
        ordering = ['name']
        
    def __str__(self):
        return self.name


class MaintenanceCategory(models.Model):
    """
    نموذج فئة الصيانة
    """
    name = models.CharField(
        _('اسم الفئة'),
        max_length=100,
        unique=True,
        help_text=_('اسم فئة الصيانة')
    )
    
    description = models.TextField(
        _('الوصف'),
        blank=True,
        null=True,
        help_text=_('وصف فئة الصيانة')
    )
    
    default_priority = models.CharField(
        _('الأولوية الافتراضية'),
        max_length=10,
        choices=MaintenanceRequest.PRIORITY_CHOICES,
        default='medium',
        help_text=_('الأولوية الافتراضية لهذه الفئة')
    )
    
    estimated_duration_hours = models.PositiveIntegerField(
        _('المدة المقدرة (ساعات)'),
        default=2,
        help_text=_('المدة المقدرة لإنجاز هذا النوع من الصيانة')
    )
    
    created_at = models.DateTimeField(
        _('تاريخ الإنشاء'),
        auto_now_add=True
    )

    class Meta:
        verbose_name = _('فئة صيانة')
        verbose_name_plural = _('فئات الصيانة')
        ordering = ['name']
        
    def __str__(self):
        return self.name


class MaintenanceSchedule(models.Model):
    """
    نموذج جدولة الصيانة الدورية
    """
    FREQUENCY_CHOICES = [
        ('weekly', _('أسبوعي')),
        ('monthly', _('شهري')),
        ('quarterly', _('ربع سنوي')),
        ('semi_annual', _('نصف سنوي')),
        ('annual', _('سنوي')),
    ]
    
    unit = models.ForeignKey(
        Unit,
        on_delete=models.CASCADE,
        related_name='maintenance_schedules',
        verbose_name=_('الوحدة'),
        help_text=_('الوحدة المراد جدولة صيانتها')
    )
    
    category = models.ForeignKey(
        MaintenanceCategory,
        on_delete=models.CASCADE,
        related_name='schedules',
        verbose_name=_('فئة الصيانة'),
        help_text=_('فئة الصيانة المجدولة')
    )
    
    title = models.CharField(
        _('عنوان الجدولة'),
        max_length=200,
        help_text=_('عنوان الصيانة المجدولة')
    )
    
    description = models.TextField(
        _('الوصف'),
        help_text=_('وصف الصيانة المجدولة')
    )
    
    frequency = models.CharField(
        _('التكرار'),
        max_length=20,
        choices=FREQUENCY_CHOICES,
        help_text=_('تكرار الصيانة')
    )
    
    next_due_date = models.DateField(
        _('تاريخ الاستحقاق التالي'),
        help_text=_('تاريخ الصيانة التالية المجدولة')
    )
    
    is_active = models.BooleanField(
        _('نشط'),
        default=True,
        help_text=_('هل الجدولة نشطة؟')
    )
    
    auto_create_requests = models.BooleanField(
        _('إنشاء طلبات تلقائي'),
        default=True,
        help_text=_('إنشاء طلبات صيانة تلقائياً حسب الجدولة')
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
        verbose_name = _('جدولة صيانة')
        verbose_name_plural = _('جدولة الصيانة')
        ordering = ['next_due_date']
        
    def __str__(self):
        return f"جدولة {self.title} - {self.unit}"

