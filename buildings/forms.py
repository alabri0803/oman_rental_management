from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Building, Floor, Unit, UnitType


class BuildingForm(forms.ModelForm):
    """نموذج إضافة وتعديل المباني"""
    
    class Meta:
        model = Building
        fields = [
            'name', 'address', 'description', 'total_floors',
            'has_mosque', 'has_elevator', 'has_parking', 'parking_spaces'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('اسم المبنى')
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('العنوان الكامل للمبنى')
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': _('وصف تفصيلي للمبنى وخدماته')
            }),
            'total_floors': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 50
            }),
            'has_mosque': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'has_elevator': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'has_parking': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'parking_spaces': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # إضافة CSS classes للحقول
        for field_name, field in self.fields.items():
            if field_name in ['has_mosque', 'has_elevator', 'has_parking']:
                continue
            field.widget.attrs.update({'class': 'form-control'})


class FloorForm(forms.ModelForm):
    """نموذج إضافة وتعديل الطوابق"""
    
    class Meta:
        model = Floor
        fields = ['floor_number', 'name', 'description']
        widgets = {
            'floor_number': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': -2,  # للطوابق السفلية
                'max': 50
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('اسم الطابق (اختياري)')
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('وصف الطابق (اختياري)')
            }),
        }


class UnitForm(forms.ModelForm):
    """نموذج إضافة وتعديل الوحدات"""
    
    class Meta:
        model = Unit
        fields = [
            'floor', 'unit_type', 'unit_number', 'area', 'rent_price',
            'bedrooms', 'bathrooms', 'has_balcony', 'has_kitchen',
            'status', 'description'
        ]
        widgets = {
            'floor': forms.Select(attrs={
                'class': 'form-select'
            }),
            'unit_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'unit_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('رقم الوحدة')
            }),
            'area': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'step': 0.1,
                'placeholder': _('المساحة بالمتر المربع')
            }),
            'rent_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'step': 0.01,
                'placeholder': _('سعر الإيجار الشهري')
            }),
            'bedrooms': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 10
            }),
            'bathrooms': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 10
            }),
            'has_balcony': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'has_kitchen': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': _('وصف الوحدة ومميزاتها')
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # تحديث خيارات الطوابق لتشمل اسم المبنى
        self.fields['floor'].queryset = Floor.objects.select_related('building').all()
        self.fields['floor'].empty_label = _('اختر الطابق')
        
        # تحديث خيارات أنواع الوحدات
        self.fields['unit_type'].queryset = UnitType.objects.all()
        self.fields['unit_type'].empty_label = _('اختر نوع الوحدة')


class UnitSearchForm(forms.Form):
    """نموذج البحث في الوحدات"""
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('البحث في الوحدات...')
        })
    )
    
    building = forms.ModelChoiceField(
        queryset=Building.objects.all(),
        required=False,
        empty_label=_('جميع المباني'),
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    status = forms.ChoiceField(
        choices=[('', _('جميع الحالات'))] + Unit.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    unit_type = forms.ModelChoiceField(
        queryset=UnitType.objects.all(),
        required=False,
        empty_label=_('جميع الأنواع'),
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    min_price = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': _('الحد الأدنى للسعر')
        })
    )
    
    max_price = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': _('الحد الأقصى للسعر')
        })
    )


class BuildingSearchForm(forms.Form):
    """نموذج البحث في المباني"""
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('البحث في المباني...')
        })
    )
    
    has_mosque = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    
    has_elevator = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    
    has_parking = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )


class UnitTypeForm(forms.ModelForm):
    """نموذج إضافة وتعديل أنواع الوحدات"""
    
    class Meta:
        model = UnitType
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('اسم نوع الوحدة')
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('وصف نوع الوحدة')
            }),
        }

