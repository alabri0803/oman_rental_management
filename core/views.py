from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Count, Sum
from buildings.models import Building, Unit
from tenants.models import Tenant
from leases.models import Lease
from payments.models import Payment


def home(request):
    """الصفحة الرئيسية للنظام مع لوحة المعلومات"""
    
    # إحصائيات عامة
    context = {
        'total_buildings': Building.objects.count(),
        'total_units': Unit.objects.count(),
        'occupied_units': Unit.objects.filter(status='rented').count(),
        'total_tenants': Tenant.objects.filter(is_active=True).count(),
        'active_leases': Lease.objects.filter(status='active').count(),
    }
    
    # حساب الإيرادات الشهرية
    monthly_revenue = Lease.objects.filter(status='active').aggregate(
        total=Sum('rent_amount')
    )['total'] or 0
    context['monthly_revenue'] = monthly_revenue
    
    # حساب معدل الإشغال
    if context['total_units'] > 0:
        context['occupancy_rate'] = round(
            (context['occupied_units'] / context['total_units']) * 100, 1
        )
    else:
        context['occupancy_rate'] = 0
    
    return render(request, 'home.html', context)

