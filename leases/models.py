from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from datetime import date, timedelta
from buildings.models import Unit
from tenants.models import Tenant


class Lease(models.Model):
    """
    نموذج عقد الإيجار
    """
    STATUS_CHOICES = [
        ('draft', _('مسودة')),
        ('active', _('نشط')),
        ('expired', _('منتهي الصلاحية')),
        ('terminated', _('مفسوخ')),
        ('renewed', _('مجدد')),
    ]
    
    PAYMENT_FREQUENCY_CHOICES = [
        ('monthly', _('شهري')),
        ('quarterly', _('ربع سنوي')),
        ('semi_annual', _('نصف سنوي')),
        ('annual', _('سنوي')),
    ]
    
    unit = models.ForeignKey(
        Unit,
        on_delete=models.CASCADE,
        related_name='leases',
        verbose_name=_('الوحدة'),
        help_text=_('الوحدة المؤجرة')
    )
    
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='leases',
        verbose_name=_('المستأجر'),
        help_text=_('المستأجر')
    )
    
    lease_number = models.CharField(
        _('رقم العقد'),
        max_length=50,
        unique=True,
        help_text=_('رقم عقد الإيجار الفريد')
    )
    
    start_date = models.DateField(
        _('تاريخ بداية العقد'),
        help_text=_('تاريخ بداية عقد الإيجار')
    )
    
    end_date = models.DateField(
        _('تاريخ انتهاء العقد'),
        help_text=_('تاريخ انتهاء عقد الإيجار')
    )
    
    rent_amount = models.DecimalField(
        _('مبلغ الإيجار الشهري'),
        max_digits=10,
        decimal_places=3,
        help_text=_('مبلغ الإيجار الشهري بالريال العماني')
    )
    
    deposit_amount = models.DecimalField(
        _('مبلغ التأمين'),
        max_digits=10,
        decimal_places=3,
        help_text=_('مبلغ التأمين المدفوع بالريال العماني')
    )
    
    payment_frequency = models.CharField(
        _('تكرار الدفع'),
        max_length=20,
        choices=PAYMENT_FREQUENCY_CHOICES,
        default='monthly',
        help_text=_('تكرار دفع الإيجار')
    )
    
    status = models.CharField(
        _('حالة العقد'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        help_text=_('الحالة الحالية للعقد')
    )
    
    contract_file = models.FileField(
        _('ملف العقد'),
        upload_to='lease_contracts/',
        blank=True,
        null=True,
        help_text=_('ملف عقد الإيجار الموقع')
    )
    
    terms_and_conditions = models.TextField(
        _('الشروط والأحكام'),
        blank=True,
        null=True,
        help_text=_('الشروط والأحكام الخاصة بالعقد')
    )
    
    notes = models.TextField(
        _('ملاحظات'),
        blank=True,
        null=True,
        help_text=_('ملاحظات إضافية حول العقد')
    )
    
    auto_renew = models.BooleanField(
        _('التجديد التلقائي'),
        default=False,
        help_text=_('هل يتم تجديد العقد تلقائياً؟')
    )
    
    renewal_notice_days = models.PositiveIntegerField(
        _('أيام إشعار التجديد'),
        default=30,
        help_text=_('عدد الأيام قبل انتهاء العقد لإرسال إشعار التجديد')
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
        verbose_name = _('عقد إيجار')
        verbose_name_plural = _('عقود الإيجار')
        ordering = ['-start_date']
        
    def __str__(self):
        return f"عقد {self.lease_number} - {self.tenant.full_name} - {self.unit}"
    
    def clean(self):
        """التحقق من صحة البيانات"""
        if self.start_date and self.end_date:
            if self.start_date >= self.end_date:
                raise ValidationError(_('تاريخ البداية يجب أن يكون قبل تاريخ الانتهاء'))
        
        # التحقق من عدم تداخل العقود للوحدة نفسها
        if self.unit:
            overlapping_leases = Lease.objects.filter(
                unit=self.unit,
                status__in=['active', 'draft']
            ).exclude(pk=self.pk)
            
            for lease in overlapping_leases:
                if (self.start_date <= lease.end_date and self.end_date >= lease.start_date):
                    raise ValidationError(
                        _('يوجد عقد آخر نشط أو مسودة لهذه الوحدة في نفس الفترة الزمنية')
                    )
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        
        # تحديث حالة الوحدة
        if self.status == 'active':
            self.unit.status = 'rented'
            self.unit.save()
        elif self.status in ['expired', 'terminated']:
            self.unit.status = 'vacant'
            self.unit.save()
    
    @property
    def duration_months(self):
        """حساب مدة العقد بالأشهر"""
        if self.start_date and self.end_date:
            return (self.end_date.year - self.start_date.year) * 12 + (self.end_date.month - self.start_date.month)
        return 0
    
    @property
    def is_active(self):
        """فحص ما إذا كان العقد نشطاً"""
        return self.status == 'active'
    
    @property
    def is_expired(self):
        """فحص ما إذا كان العقد منتهي الصلاحية"""
        return self.end_date < date.today() if self.end_date else False
    
    @property
    def days_until_expiry(self):
        """حساب عدد الأيام المتبقية حتى انتهاء العقد"""
        if self.end_date:
            return (self.end_date - date.today()).days
        return None
    
    @property
    def needs_renewal_notice(self):
        """فحص ما إذا كان العقد يحتاج إشعار تجديد"""
        if self.days_until_expiry is not None:
            return self.days_until_expiry <= self.renewal_notice_days
        return False


class LeaseRenewal(models.Model):
    """
    نموذج تجديد عقد الإيجار
    """
    original_lease = models.ForeignKey(
        Lease,
        on_delete=models.CASCADE,
        related_name='renewals',
        verbose_name=_('العقد الأصلي'),
        help_text=_('العقد الأصلي المراد تجديده')
    )
    
    new_lease = models.OneToOneField(
        Lease,
        on_delete=models.CASCADE,
        related_name='renewal_record',
        verbose_name=_('العقد الجديد'),
        help_text=_('العقد الجديد بعد التجديد')
    )
    
    renewal_date = models.DateField(
        _('تاريخ التجديد'),
        default=date.today,
        help_text=_('تاريخ تجديد العقد')
    )
    
    rent_increase_percentage = models.DecimalField(
        _('نسبة زيادة الإيجار (%)'),
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text=_('نسبة زيادة الإيجار عند التجديد')
    )
    
    notes = models.TextField(
        _('ملاحظات'),
        blank=True,
        null=True,
        help_text=_('ملاحظات حول التجديد')
    )
    
    created_at = models.DateTimeField(
        _('تاريخ الإنشاء'),
        auto_now_add=True
    )

    class Meta:
        verbose_name = _('تجديد عقد')
        verbose_name_plural = _('تجديدات العقود')
        ordering = ['-renewal_date']
        
    def __str__(self):
        return f"تجديد عقد {self.original_lease.lease_number} - {self.renewal_date}"


class LeaseTermination(models.Model):
    """
    نموذج إنهاء عقد الإيجار
    """
    TERMINATION_REASONS = [
        ('tenant_request', _('طلب من المستأجر')),
        ('owner_request', _('طلب من المالك')),
        ('breach_of_contract', _('مخالفة شروط العقد')),
        ('non_payment', _('عدم دفع الإيجار')),
        ('property_sale', _('بيع العقار')),
        ('renovation', _('تجديد العقار')),
        ('other', _('أخرى')),
    ]
    
    lease = models.OneToOneField(
        Lease,
        on_delete=models.CASCADE,
        related_name='termination',
        verbose_name=_('العقد'),
        help_text=_('العقد المراد إنهاؤه')
    )
    
    termination_date = models.DateField(
        _('تاريخ الإنهاء'),
        help_text=_('تاريخ إنهاء العقد')
    )
    
    reason = models.CharField(
        _('سبب الإنهاء'),
        max_length=50,
        choices=TERMINATION_REASONS,
        help_text=_('سبب إنهاء العقد')
    )
    
    notice_period_days = models.PositiveIntegerField(
        _('فترة الإشعار (أيام)'),
        default=30,
        help_text=_('فترة الإشعار المطلوبة قبل الإنهاء')
    )
    
    penalty_amount = models.DecimalField(
        _('مبلغ الغرامة'),
        max_digits=10,
        decimal_places=3,
        default=0,
        help_text=_('مبلغ الغرامة المترتبة على الإنهاء المبكر')
    )
    
    deposit_refund_amount = models.DecimalField(
        _('مبلغ استرداد التأمين'),
        max_digits=10,
        decimal_places=3,
        default=0,
        help_text=_('مبلغ التأمين المسترد للمستأجر')
    )
    
    notes = models.TextField(
        _('ملاحظات'),
        blank=True,
        null=True,
        help_text=_('ملاحظات حول إنهاء العقد')
    )
    
    created_at = models.DateTimeField(
        _('تاريخ الإنشاء'),
        auto_now_add=True
    )

    class Meta:
        verbose_name = _('إنهاء عقد')
        verbose_name_plural = _('إنهاءات العقود')
        ordering = ['-termination_date']
        
    def __str__(self):
        return f"إنهاء عقد {self.lease.lease_number} - {self.termination_date}"

