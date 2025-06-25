from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Tenant, TenantDocument
from .forms import TenantForm, TenantDocumentForm


def tenant_list(request):
    """قائمة المستأجرين مع البحث والفلترة"""
    tenants = Tenant.objects.all()
    
    # البحث
    search_query = request.GET.get('search')
    if search_query:
        tenants = tenants.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(national_id__icontains=search_query) |
            Q(phone_number__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    # الفلترة
    nationality = request.GET.get('nationality')
    if nationality:
        tenants = tenants.filter(nationality=nationality)
    
    gender = request.GET.get('gender')
    if gender:
        tenants = tenants.filter(gender=gender)
    
    marital_status = request.GET.get('marital_status')
    if marital_status:
        tenants = tenants.filter(marital_status=marital_status)
    
    is_active = request.GET.get('is_active')
    if is_active:
        tenants = tenants.filter(is_active=is_active == 'true')
    
    # الترتيب
    sort_by = request.GET.get('sort', 'first_name')
    tenants = tenants.order_by(sort_by)
    
    # الترقيم
    paginator = Paginator(tenants, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # البيانات للفلاتر
    nationalities = Tenant.objects.values_list('nationality', flat=True).distinct()
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'nationalities': nationalities,
        'selected_nationality': nationality,
        'selected_gender': gender,
        'selected_marital_status': marital_status,
        'selected_is_active': is_active,
        'sort_by': sort_by,
    }
    
    return render(request, 'tenants/tenant_list.html', context)


def tenant_detail(request, tenant_id):
    """تفاصيل المستأجر"""
    tenant = get_object_or_404(Tenant, id=tenant_id)
    
    # العقود الحالية والسابقة
    current_leases = []
    past_leases = []
    if hasattr(tenant, 'lease_set'):
        current_leases = tenant.lease_set.filter(status='active')
        past_leases = tenant.lease_set.exclude(status='active')[:5]
    
    # الوثائق
    documents = tenant.tenantdocument_set.all()
    
    # الدفعات الأخيرة
    recent_payments = []
    if current_leases:
        for lease in current_leases:
            if hasattr(lease, 'payment_set'):
                payments = lease.payment_set.all()[:3]
                recent_payments.extend(payments)
    
    context = {
        'tenant': tenant,
        'current_leases': current_leases,
        'past_leases': past_leases,
        'documents': documents,
        'recent_payments': recent_payments,
    }
    
    return render(request, 'tenants/tenant_detail.html', context)


@login_required
def tenant_create(request):
    """إضافة مستأجر جديد"""
    if request.method == 'POST':
        form = TenantForm(request.POST)
        if form.is_valid():
            tenant = form.save()
            messages.success(request, _('تم إضافة المستأجر بنجاح'))
            return redirect('tenants:detail', tenant_id=tenant.id)
    else:
        form = TenantForm()
    
    return render(request, 'tenants/tenant_form.html', {
        'form': form,
        'title': _('إضافة مستأجر جديد')
    })


@login_required
def tenant_edit(request, tenant_id):
    """تعديل المستأجر"""
    tenant = get_object_or_404(Tenant, id=tenant_id)
    
    if request.method == 'POST':
        form = TenantForm(request.POST, instance=tenant)
        if form.is_valid():
            form.save()
            messages.success(request, _('تم تحديث بيانات المستأجر بنجاح'))
            return redirect('tenants:detail', tenant_id=tenant.id)
    else:
        form = TenantForm(instance=tenant)
    
    return render(request, 'tenants/tenant_form.html', {
        'form': form,
        'tenant': tenant,
        'title': _('تعديل بيانات المستأجر')
    })


@login_required
def tenant_delete(request, tenant_id):
    """حذف المستأجر"""
    tenant = get_object_or_404(Tenant, id=tenant_id)
    
    # التحقق من وجود عقود نشطة
    active_leases = tenant.lease_set.filter(status='active').count() if hasattr(tenant, 'lease_set') else 0
    
    if active_leases > 0:
        messages.error(request, _('لا يمكن حذف المستأجر لوجود عقود نشطة'))
        return redirect('tenants:detail', tenant_id=tenant.id)
    
    if request.method == 'POST':
        tenant_name = tenant.full_name
        tenant.delete()
        messages.success(request, _('تم حذف المستأجر "{}" بنجاح').format(tenant_name))
        return redirect('tenants:list')
    
    return render(request, 'tenants/tenant_confirm_delete.html', {
        'tenant': tenant,
        'active_leases': active_leases
    })


@login_required
def tenant_deactivate(request, tenant_id):
    """إلغاء تفعيل المستأجر"""
    tenant = get_object_or_404(Tenant, id=tenant_id)
    
    if request.method == 'POST':
        tenant.is_active = False
        tenant.save()
        messages.success(request, _('تم إلغاء تفعيل المستأجر بنجاح'))
        return redirect('tenants:detail', tenant_id=tenant.id)
    
    return render(request, 'tenants/tenant_confirm_deactivate.html', {
        'tenant': tenant
    })


@login_required
def tenant_activate(request, tenant_id):
    """تفعيل المستأجر"""
    tenant = get_object_or_404(Tenant, id=tenant_id)
    tenant.is_active = True
    tenant.save()
    messages.success(request, _('تم تفعيل المستأجر بنجاح'))
    return redirect('tenants:detail', tenant_id=tenant.id)


@login_required
def document_upload(request, tenant_id):
    """رفع وثيقة للمستأجر"""
    tenant = get_object_or_404(Tenant, id=tenant_id)
    
    if request.method == 'POST':
        form = TenantDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.tenant = tenant
            document.save()
            messages.success(request, _('تم رفع الوثيقة بنجاح'))
            return redirect('tenants:detail', tenant_id=tenant.id)
    else:
        form = TenantDocumentForm()
    
    return render(request, 'tenants/document_upload.html', {
        'form': form,
        'tenant': tenant,
        'title': _('رفع وثيقة جديدة')
    })


@login_required
def document_delete(request, tenant_id, document_id):
    """حذف وثيقة المستأجر"""
    tenant = get_object_or_404(Tenant, id=tenant_id)
    document = get_object_or_404(TenantDocument, id=document_id, tenant=tenant)
    
    if request.method == 'POST':
        document_title = document.title
        document.delete()
        messages.success(request, _('تم حذف الوثيقة "{}" بنجاح').format(document_title))
        return redirect('tenants:detail', tenant_id=tenant.id)
    
    return render(request, 'tenants/document_confirm_delete.html', {
        'tenant': tenant,
        'document': document
    })


def tenant_search_ajax(request):
    """البحث في المستأجرين عبر AJAX"""
    query = request.GET.get('q', '')
    
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    tenants = Tenant.objects.filter(
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query) |
        Q(national_id__icontains=query) |
        Q(phone_number__icontains=query)
    ).filter(is_active=True)[:10]
    
    results = []
    for tenant in tenants:
        results.append({
            'id': tenant.id,
            'text': f"{tenant.full_name} - {tenant.national_id}",
            'phone': tenant.phone_number,
            'email': tenant.email or '',
        })
    
    return JsonResponse({'results': results})


def tenant_statistics(request):
    """إحصائيات المستأجرين"""
    total_tenants = Tenant.objects.count()
    active_tenants = Tenant.objects.filter(is_active=True).count()
    inactive_tenants = total_tenants - active_tenants
    
    # إحصائيات حسب الجنسية
    nationality_stats = Tenant.objects.values('nationality').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # إحصائيات حسب الجنس
    gender_stats = Tenant.objects.values('gender').annotate(
        count=Count('id')
    )
    
    # إحصائيات حسب الحالة الاجتماعية
    marital_stats = Tenant.objects.values('marital_status').annotate(
        count=Count('id')
    )
    
    context = {
        'total_tenants': total_tenants,
        'active_tenants': active_tenants,
        'inactive_tenants': inactive_tenants,
        'nationality_stats': nationality_stats,
        'gender_stats': gender_stats,
        'marital_stats': marital_stats,
    }
    
    return render(request, 'tenants/tenant_statistics.html', context)

