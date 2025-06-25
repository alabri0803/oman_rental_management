from django import forms
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from .models import Tenant, TenantDocument


class TenantForm(forms.ModelForm):
    """نموذج إضافة وتعديل المستأجرين"""
    
    # التحقق من رقم الهوية العمانية
    national_id_validator = RegexValidator(
        regex=r'^\d{8}$',
        message=_('رقم الهوية يجب أن يكون 8 أرقام')
    )
    
    # التحقق من رقم الهاتف العماني
    phone_validator = RegexValidator(
        regex=r'^(\+968|968|00968)?\s?[79]\d{7}$',
        message=_('رقم الهاتف غير صحيح. يجب أن يبدأ بـ 7 أو 9 ويتكون من 8 أرقام')
    )
    
    class Meta:
        model = Tenant
        fields = [
            'first_name', 'last_name', 'national_id', 'date_of_birth',
            'gender', 'marital_status', 'phone_number', 'email', 'address',
            'nationality', 'occupation', 'employer', 'monthly_income',
            'emergency_contact_name', 'emergency_contact_phone', 
            'emergency_contact_relationship', 'notes', 'is_active', 'user'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('الاسم الأول')
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('اسم العائلة')
            }),
            'national_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('رقم الهوية (8 أرقام)'),
                'maxlength': 8
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'gender': forms.Select(attrs={
                'class': 'form-select'
            }),
            'marital_status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('رقم الهاتف (مثال: 91234567)')
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': _('البريد الإلكتروني')
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('العنوان الكامل')
            }),
            'nationality': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('الجنسية'),
                'value': 'عماني'
            }),
            'occupation': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('المهنة')
            }),
            'employer': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('جهة العمل')
            }),
            'monthly_income': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'step': 0.01,
                'placeholder': _('الراتب الشهري (ر.ع)')
            }),
            'emergency_contact_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('اسم جهة الاتصال في الطوارئ')
            }),
            'emergency_contact_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('رقم هاتف جهة الاتصال')
            }),
            'emergency_contact_relationship': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('صلة القرابة')
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': _('ملاحظات إضافية')
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'user': forms.Select(attrs={
                'class': 'form-select'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # إضافة validators
        self.fields['national_id'].validators.append(self.national_id_validator)
        self.fields['phone_number'].validators.append(self.phone_validator)
        
        # جعل بعض الحقول اختيارية في النموذج
        self.fields['email'].required = False
        self.fields['user'].required = False
        self.fields['employer'].required = False
        self.fields['monthly_income'].required = False
        self.fields['emergency_contact_name'].required = False
        self.fields['emergency_contact_phone'].required = False
        self.fields['emergency_contact_relationship'].required = False
        self.fields['notes'].required = False
        
        # تحديث خيارات المستخدمين
        self.fields['user'].empty_label = _('اختر مستخدم (اختياري)')
    
    def clean_national_id(self):
        """التحقق من عدم تكرار رقم الهوية"""
        national_id = self.cleaned_data.get('national_id')
        
        if national_id:
            # التحقق من عدم وجود رقم الهوية مسبقاً
            existing_tenant = Tenant.objects.filter(national_id=national_id)
            if self.instance.pk:
                existing_tenant = existing_tenant.exclude(pk=self.instance.pk)
            
            if existing_tenant.exists():
                raise forms.ValidationError(_('رقم الهوية موجود مسبقاً'))
        
        return national_id
    
    def clean_email(self):
        """التحقق من عدم تكرار البريد الإلكتروني"""
        email = self.cleaned_data.get('email')
        
        if email:
            existing_tenant = Tenant.objects.filter(email=email)
            if self.instance.pk:
                existing_tenant = existing_tenant.exclude(pk=self.instance.pk)
            
            if existing_tenant.exists():
                raise forms.ValidationError(_('البريد الإلكتروني موجود مسبقاً'))
        
        return email


class TenantDocumentForm(forms.ModelForm):
    """نموذج رفع وثائق المستأجر"""
    
    class Meta:
        model = TenantDocument
        fields = ['document_type', 'title', 'file', 'description']
        widgets = {
            'document_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('عنوان الوثيقة')
            }),
            'file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png,.doc,.docx'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('وصف الوثيقة (اختياري)')
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['description'].required = False


class TenantSearchForm(forms.Form):
    """نموذج البحث في المستأجرين"""
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('البحث في المستأجرين...')
        })
    )
    
    nationality = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('الجنسية')
        })
    )
    
    gender = forms.ChoiceField(
        choices=[('', _('جميع الأجناس'))] + Tenant.GENDER_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    marital_status = forms.ChoiceField(
        choices=[('', _('جميع الحالات الاجتماعية'))] + Tenant.MARITAL_STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    is_active = forms.ChoiceField(
        choices=[
            ('', _('جميع المستأجرين')),
            ('true', _('النشطون فقط')),
            ('false', _('غير النشطين فقط'))
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    min_income = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': _('الحد الأدنى للراتب')
        })
    )
    
    max_income = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': _('الحد الأقصى للراتب')
        })
    )


class TenantQuickAddForm(forms.ModelForm):
    """نموذج الإضافة السريعة للمستأجر"""
    
    class Meta:
        model = Tenant
        fields = [
            'first_name', 'last_name', 'national_id', 
            'phone_number', 'email', 'nationality'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': _('الاسم الأول')
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': _('اسم العائلة')
            }),
            'national_id': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': _('رقم الهوية'),
                'maxlength': 8
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': _('رقم الهاتف')
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': _('البريد الإلكتروني')
            }),
            'nationality': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': _('الجنسية'),
                'value': 'عماني'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = False

