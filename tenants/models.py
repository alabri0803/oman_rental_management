from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from core.models import User


class Tenant(models.Model):
    """
    نموذج المستأجر
    """
    GENDER_CHOICES = [
        ('male', _('ذكر')),
        ('female', _('أنثى')),
    ]
    
    MARITAL_STATUS_CHOICES = [
        ('single', _('أعزب')),
        ('married', _('متزوج')),
        ('divorced', _('مطلق')),
        ('widowed', _('أرمل')),
    ]
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='tenant_profile',
        verbose_name=_('المستخدم'),
        blank=True,
        null=True,
        help_text=_('ربط المستأجر بحساب مستخدم في النظام (اختياري)')
    )
    
    first_name = models.CharField(
        _('الاسم الأول'),
        max_length=100,
        help_text=_('الاسم الأول للمستأجر')
    )
    
    last_name = models.CharField(
        _('اسم العائلة'),
        max_length=100,
        help_text=_('اسم العائلة للمستأجر')
    )
    
    national_id = models.CharField(
        _('الرقم المدني'),
        max_length=20,
        unique=True,
        help_text=_('الرقم المدني أو رقم البطاقة الشخصية')
    )
    
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message=_("رقم الهاتف يجب أن يكون بالصيغة: '+999999999'. يُسمح بحد أقصى 15 رقم.")
    )
    
    phone_number = models.CharField(
        _('رقم الهاتف'),
        validators=[phone_regex],
        max_length=17,
        help_text=_('رقم الهاتف للمستأجر')
    )
    
    email = models.EmailField(
        _('البريد الإلكتروني'),
        help_text=_('البريد الإلكتروني للمستأجر')
    )
    
    address = models.TextField(
        _('العنوان'),
        help_text=_('عنوان المستأجر الحالي')
    )
    
    nationality = models.CharField(
        _('الجنسية'),
        max_length=50,
        help_text=_('جنسية المستأجر')
    )
    
    gender = models.CharField(
        _('الجنس'),
        max_length=10,
        choices=GENDER_CHOICES,
        help_text=_('جنس المستأجر')
    )
    
    date_of_birth = models.DateField(
        _('تاريخ الميلاد'),
        help_text=_('تاريخ ميلاد المستأجر')
    )
    
    marital_status = models.CharField(
        _('الحالة الاجتماعية'),
        max_length=20,
        choices=MARITAL_STATUS_CHOICES,
        help_text=_('الحالة الاجتماعية للمستأجر')
    )
    
    occupation = models.CharField(
        _('المهنة'),
        max_length=100,
        blank=True,
        null=True,
        help_text=_('مهنة المستأجر')
    )
    
    employer = models.CharField(
        _('جهة العمل'),
        max_length=200,
        blank=True,
        null=True,
        help_text=_('اسم جهة العمل')
    )
    
    monthly_income = models.DecimalField(
        _('الراتب الشهري'),
        max_digits=10,
        decimal_places=3,
        blank=True,
        null=True,
        help_text=_('الراتب الشهري بالريال العماني')
    )
    
    emergency_contact_name = models.CharField(
        _('اسم جهة الاتصال في حالات الطوارئ'),
        max_length=200,
        help_text=_('اسم الشخص للاتصال به في حالات الطوارئ')
    )
    
    emergency_contact_phone = models.CharField(
        _('رقم هاتف جهة الاتصال في حالات الطوارئ'),
        validators=[phone_regex],
        max_length=17,
        help_text=_('رقم هاتف جهة الاتصال في حالات الطوارئ')
    )
    
    emergency_contact_relationship = models.CharField(
        _('صلة القرابة مع جهة الاتصال'),
        max_length=100,
        help_text=_('صلة القرابة مع جهة الاتصال في حالات الطوارئ')
    )
    
    notes = models.TextField(
        _('ملاحظات'),
        blank=True,
        null=True,
        help_text=_('ملاحظات إضافية حول المستأجر')
    )
    
    is_active = models.BooleanField(
        _('نشط'),
        default=True,
        help_text=_('هل المستأجر نشط في النظام؟')
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
        verbose_name = _('مستأجر')
        verbose_name_plural = _('المستأجرون')
        ordering = ['last_name', 'first_name']
        
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        """إرجاع الاسم الكامل للمستأجر"""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def age(self):
        """حساب عمر المستأجر"""
        from datetime import date
        today = date.today()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))


class TenantDocument(models.Model):
    """
    نموذج وثائق المستأجر
    """
    DOCUMENT_TYPES = [
        ('id_copy', _('نسخة من البطاقة الشخصية')),
        ('passport', _('نسخة من جواز السفر')),
        ('salary_certificate', _('شهادة راتب')),
        ('bank_statement', _('كشف حساب بنكي')),
        ('employment_letter', _('خطاب من جهة العمل')),
        ('other', _('أخرى')),
    ]
    
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name=_('المستأجر'),
        help_text=_('المستأجر الذي تنتمي إليه الوثيقة')
    )
    
    document_type = models.CharField(
        _('نوع الوثيقة'),
        max_length=50,
        choices=DOCUMENT_TYPES,
        help_text=_('نوع الوثيقة')
    )
    
    title = models.CharField(
        _('عنوان الوثيقة'),
        max_length=200,
        help_text=_('عنوان أو اسم الوثيقة')
    )
    
    file = models.FileField(
        _('الملف'),
        upload_to='tenant_documents/',
        help_text=_('ملف الوثيقة')
    )
    
    description = models.TextField(
        _('الوصف'),
        blank=True,
        null=True,
        help_text=_('وصف إضافي للوثيقة')
    )
    
    uploaded_at = models.DateTimeField(
        _('تاريخ الرفع'),
        auto_now_add=True
    )

    class Meta:
        verbose_name = _('وثيقة مستأجر')
        verbose_name_plural = _('وثائق المستأجرين')
        ordering = ['-uploaded_at']
        
    def __str__(self):
        return f"{self.tenant.full_name} - {self.title}"

