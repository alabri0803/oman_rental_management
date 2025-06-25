from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from datetime import date, timedelta
from leases.models import Lease


class Payment(models.Model):
    """
    نموذج الدفعة
    """
    PAYMENT_TYPES = [
        ('rent', _('إيجار')),
        ('deposit', _('تأمين')),
        ('maintenance', _('صيانة')),
        ('utilities', _('خدمات')),
        ('penalty', _('غرامة')),
        ('other', _('أخرى')),
    ]
    
    PAYMENT_METHODS = [
        ('cash', _('نقداً')),
        ('bank_transfer', _('تحويل بنكي')),
        ('check', _('شيك')),
        ('credit_card', _('بطاقة ائتمان')),
        ('online', _('دفع إلكتروني')),
    ]
    
    STATUS_CHOICES = [
        ('pending', _('معلق')),
        ('paid', _('مدفوع')),
        ('overdue', _('متأخر')),
        ('cancelled', _('ملغى')),
        ('refunded', _('مسترد')),
    ]
    
    lease = models.ForeignKey(
        Lease,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name=_('عقد الإيجار'),
        help_text=_('عقد الإيجار المرتبط بالدفعة')
    )
    
    payment_type = models.CharField(
        _('نوع الدفعة'),
        max_length=20,
        choices=PAYMENT_TYPES,
        default='rent',
        help_text=_('نوع الدفعة')
    )
    
    amount = models.DecimalField(
        _('المبلغ'),
        max_digits=10,
        decimal_places=3,
        help_text=_('مبلغ الدفعة بالريال العماني')
    )
    
    due_date = models.DateField(
        _('تاريخ الاستحقاق'),
        help_text=_('تاريخ استحقاق الدفعة')
    )
    
    payment_date = models.DateField(
        _('تاريخ الدفع'),
        blank=True,
        null=True,
        help_text=_('تاريخ دفع المبلغ الفعلي')
    )
    
    payment_method = models.CharField(
        _('طريقة الدفع'),
        max_length=20,
        choices=PAYMENT_METHODS,
        blank=True,
        null=True,
        help_text=_('طريقة الدفع المستخدمة')
    )
    
    status = models.CharField(
        _('حالة الدفعة'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text=_('حالة الدفعة الحالية')
    )
    
    reference_number = models.CharField(
        _('رقم المرجع'),
        max_length=100,
        blank=True,
        null=True,
        help_text=_('رقم مرجع الدفعة (رقم الشيك، رقم التحويل، إلخ)')
    )
    
    receipt_number = models.CharField(
        _('رقم الإيصال'),
        max_length=50,
        unique=True,
        blank=True,
        null=True,
        help_text=_('رقم إيصال الدفعة')
    )
    
    late_fee = models.DecimalField(
        _('رسوم التأخير'),
        max_digits=10,
        decimal_places=3,
        default=0,
        help_text=_('رسوم التأخير المضافة للدفعة')
    )
    
    discount = models.DecimalField(
        _('الخصم'),
        max_digits=10,
        decimal_places=3,
        default=0,
        help_text=_('مبلغ الخصم المطبق على الدفعة')
    )
    
    notes = models.TextField(
        _('ملاحظات'),
        blank=True,
        null=True,
        help_text=_('ملاحظات إضافية حول الدفعة')
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
        verbose_name = _('دفعة')
        verbose_name_plural = _('الدفعات')
        ordering = ['-due_date']
        
    def __str__(self):
        return f"دفعة {self.get_payment_type_display()} - {self.lease.tenant.full_name} - {self.amount} ر.ع"
    
    def clean(self):
        """التحقق من صحة البيانات"""
        if self.payment_date and self.due_date:
            if self.payment_date < self.due_date and self.status == 'paid':
                # دفعة مبكرة - لا مشكلة
                pass
        
        if self.amount <= 0:
            raise ValidationError(_('مبلغ الدفعة يجب أن يكون أكبر من صفر'))
    
    @property
    def total_amount(self):
        """حساب المبلغ الإجمالي شاملاً رسوم التأخير ناقصاً الخصم"""
        return self.amount + self.late_fee - self.discount
    
    @property
    def is_overdue(self):
        """فحص ما إذا كانت الدفعة متأخرة"""
        if self.status == 'paid':
            return False
        return self.due_date < date.today()
    
    @property
    def days_overdue(self):
        """حساب عدد أيام التأخير"""
        if self.is_overdue:
            return (date.today() - self.due_date).days
        return 0
    
    def mark_as_paid(self, payment_date=None, payment_method=None, reference_number=None):
        """تحديد الدفعة كمدفوعة"""
        self.status = 'paid'
        self.payment_date = payment_date or date.today()
        if payment_method:
            self.payment_method = payment_method
        if reference_number:
            self.reference_number = reference_number
        self.save()


class PaymentSchedule(models.Model):
    """
    نموذج جدولة الدفعات
    """
    lease = models.ForeignKey(
        Lease,
        on_delete=models.CASCADE,
        related_name='payment_schedules',
        verbose_name=_('عقد الإيجار'),
        help_text=_('عقد الإيجار المرتبط بالجدولة')
    )
    
    schedule_name = models.CharField(
        _('اسم الجدولة'),
        max_length=200,
        help_text=_('اسم وصفي لجدولة الدفعات')
    )
    
    start_date = models.DateField(
        _('تاريخ البداية'),
        help_text=_('تاريخ بداية جدولة الدفعات')
    )
    
    end_date = models.DateField(
        _('تاريخ النهاية'),
        help_text=_('تاريخ نهاية جدولة الدفعات')
    )
    
    payment_amount = models.DecimalField(
        _('مبلغ الدفعة'),
        max_digits=10,
        decimal_places=3,
        help_text=_('مبلغ كل دفعة في الجدولة')
    )
    
    frequency_days = models.PositiveIntegerField(
        _('تكرار الدفع (أيام)'),
        default=30,
        help_text=_('عدد الأيام بين كل دفعة')
    )
    
    is_active = models.BooleanField(
        _('نشط'),
        default=True,
        help_text=_('هل الجدولة نشطة؟')
    )
    
    auto_generate = models.BooleanField(
        _('إنشاء تلقائي'),
        default=True,
        help_text=_('إنشاء الدفعات تلقائياً حسب الجدولة')
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
        verbose_name = _('جدولة دفعات')
        verbose_name_plural = _('جدولة الدفعات')
        ordering = ['-start_date']
        
    def __str__(self):
        return f"جدولة {self.schedule_name} - {self.lease.tenant.full_name}"
    
    def generate_payments(self):
        """إنشاء الدفعات حسب الجدولة"""
        if not self.is_active or not self.auto_generate:
            return
        
        current_date = self.start_date
        payment_count = 0
        
        while current_date <= self.end_date:
            # فحص ما إذا كانت الدفعة موجودة مسبقاً
            existing_payment = Payment.objects.filter(
                lease=self.lease,
                due_date=current_date,
                payment_type='rent'
            ).first()
            
            if not existing_payment:
                Payment.objects.create(
                    lease=self.lease,
                    payment_type='rent',
                    amount=self.payment_amount,
                    due_date=current_date,
                    status='pending'
                )
                payment_count += 1
            
            current_date += timedelta(days=self.frequency_days)
        
        return payment_count


class Receipt(models.Model):
    """
    نموذج الإيصال
    """
    payment = models.OneToOneField(
        Payment,
        on_delete=models.CASCADE,
        related_name='receipt',
        verbose_name=_('الدفعة'),
        help_text=_('الدفعة المرتبطة بالإيصال')
    )
    
    receipt_number = models.CharField(
        _('رقم الإيصال'),
        max_length=50,
        unique=True,
        help_text=_('رقم الإيصال الفريد')
    )
    
    issued_date = models.DateField(
        _('تاريخ الإصدار'),
        default=date.today,
        help_text=_('تاريخ إصدار الإيصال')
    )
    
    issued_by = models.CharField(
        _('أصدر بواسطة'),
        max_length=200,
        help_text=_('اسم الشخص الذي أصدر الإيصال')
    )
    
    notes = models.TextField(
        _('ملاحظات'),
        blank=True,
        null=True,
        help_text=_('ملاحظات إضافية على الإيصال')
    )
    
    created_at = models.DateTimeField(
        _('تاريخ الإنشاء'),
        auto_now_add=True
    )

    class Meta:
        verbose_name = _('إيصال')
        verbose_name_plural = _('الإيصالات')
        ordering = ['-issued_date']
        
    def __str__(self):
        return f"إيصال {self.receipt_number} - {self.payment.lease.tenant.full_name}"

