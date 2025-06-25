from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    نموذج المستخدم المخصص مع حقول إضافية
    """
    phone_number = models.CharField(
        _('رقم الهاتف'),
        max_length=15,
        blank=True,
        null=True,
        help_text=_('رقم الهاتف للمستخدم')
    )
    
    nationality = models.CharField(
        _('الجنسية'),
        max_length=50,
        blank=True,
        null=True,
        help_text=_('جنسية المستخدم')
    )
    
    national_id = models.CharField(
        _('الرقم المدني'),
        max_length=20,
        blank=True,
        null=True,
        unique=True,
        help_text=_('الرقم المدني أو رقم البطاقة الشخصية')
    )
    
    address = models.TextField(
        _('العنوان'),
        blank=True,
        null=True,
        help_text=_('عنوان المستخدم')
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
        verbose_name = _('مستخدم')
        verbose_name_plural = _('المستخدمون')
        
    def __str__(self):
        return f"{self.first_name} {self.last_name}" if self.first_name and self.last_name else self.username

