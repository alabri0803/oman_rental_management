from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.decorators import login_required
from .models import Building, Floor, Unit, UnitType
from .forms import BuildingForm, FloorForm, UnitForm


def building_list(request):
    """قائمة المباني مع البحث والفلترة"""
    buildings = Building.objects.all()
    
    # البحث
    search_query = request.GET.get('search')
    if search_query:
        buildings = buildings.filter(
            Q(name__icontains=search_query) |
            Q(address__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # الفلترة
    has_mosque = request.GET.get('has_mosque')
    if has_mosque:
        buildings = buildings.filter(has_mosque=True)
    
    has_elevator = request.GET.get('has_elevator')
    if has_elevator:
        buildings = buildings.filter(has_elevator=True)
    
    has_parking = request.GET.get('has_parking')
    if has_parking:
        buildings = buildings.filter(has_parking=True)
    
    # الترقيم
    paginator = Paginator(buildings, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'has_mosque': has_mosque,
        'has_elevator': has_elevator,
        'has_parking': has_parking,
    }
    
    return render(request, 'buildings/building_list.html', context)


def building_detail(request, building_id):
    """تفاصيل المبنى"""
    building = get_object_or_404(Building, id=building_id)
    floors = building.floors.all().prefetch_related('units')
    
    # إحصائيات المبنى
    total_units = Unit.objects.filter(floor__building=building).count()
    occupied_units = Unit.objects.filter(floor__building=building, status='rented').count()
    vacant_units = Unit.objects.filter(floor__building=building, status='vacant').count()
    maintenance_units = Unit.objects.filter(floor__building=building, status='maintenance').count()
    
    occupancy_rate = (occupied_units / total_units * 100) if total_units > 0 else 0
    
    context = {
        'building': building,
        'floors': floors,
        'total_units': total_units,
        'occupied_units': occupied_units,
        'vacant_units': vacant_units,
        'maintenance_units': maintenance_units,
        'occupancy_rate': round(occupancy_rate, 1),
    }
    
    return render(request, 'buildings/building_detail.html', context)


@login_required
def building_create(request):
    """إضافة مبنى جديد"""
    if request.method == 'POST':
        form = BuildingForm(request.POST)
        if form.is_valid():
            building = form.save()
            messages.success(request, _('تم إضافة المبنى بنجاح'))
            return redirect('buildings:detail', building_id=building.id)
    else:
        form = BuildingForm()
    
    return render(request, 'buildings/building_form.html', {
        'form': form,
        'title': _('إضافة مبنى جديد')
    })


@login_required
def building_edit(request, building_id):
    """تعديل المبنى"""
    building = get_object_or_404(Building, id=building_id)
    
    if request.method == 'POST':
        form = BuildingForm(request.POST, instance=building)
        if form.is_valid():
            form.save()
            messages.success(request, _('تم تحديث المبنى بنجاح'))
            return redirect('buildings:detail', building_id=building.id)
    else:
        form = BuildingForm(instance=building)
    
    return render(request, 'buildings/building_form.html', {
        'form': form,
        'building': building,
        'title': _('تعديل المبنى')
    })


@login_required
def building_delete(request, building_id):
    """حذف المبنى"""
    building = get_object_or_404(Building, id=building_id)
    
    if request.method == 'POST':
        building_name = building.name
        building.delete()
        messages.success(request, _('تم حذف المبنى "{}" بنجاح').format(building_name))
        return redirect('buildings:list')
    
    return render(request, 'buildings/building_confirm_delete.html', {
        'building': building
    })


def unit_list(request):
    """قائمة الوحدات مع البحث والفلترة"""
    units = Unit.objects.select_related('floor__building', 'unit_type').all()
    
    # البحث
    search_query = request.GET.get('search')
    if search_query:
        units = units.filter(
            Q(unit_number__icontains=search_query) |
            Q(floor__building__name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # الفلترة
    building_id = request.GET.get('building')
    if building_id:
        units = units.filter(floor__building_id=building_id)
    
    status = request.GET.get('status')
    if status:
        units = units.filter(status=status)
    
    unit_type_id = request.GET.get('unit_type')
    if unit_type_id:
        units = units.filter(unit_type_id=unit_type_id)
    
    # الترتيب
    sort_by = request.GET.get('sort', 'floor__building__name')
    units = units.order_by(sort_by)
    
    # الترقيم
    paginator = Paginator(units, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # البيانات للفلاتر
    buildings = Building.objects.all()
    unit_types = UnitType.objects.all()
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'buildings': buildings,
        'unit_types': unit_types,
        'selected_building': building_id,
        'selected_status': status,
        'selected_unit_type': unit_type_id,
        'sort_by': sort_by,
    }
    
    return render(request, 'buildings/unit_list.html', context)


def unit_detail(request, unit_id):
    """تفاصيل الوحدة"""
    unit = get_object_or_404(Unit.objects.select_related('floor__building', 'unit_type'), id=unit_id)
    
    # العقد الحالي إن وجد
    current_lease = None
    if hasattr(unit, 'lease_set'):
        current_lease = unit.lease_set.filter(status='active').first()
    
    # تاريخ الصيانة
    maintenance_requests = []
    if hasattr(unit, 'maintenancerequest_set'):
        maintenance_requests = unit.maintenancerequest_set.all()[:5]
    
    context = {
        'unit': unit,
        'current_lease': current_lease,
        'maintenance_requests': maintenance_requests,
    }
    
    return render(request, 'buildings/unit_detail.html', context)


@login_required
def unit_create(request):
    """إضافة وحدة جديدة"""
    if request.method == 'POST':
        form = UnitForm(request.POST)
        if form.is_valid():
            unit = form.save()
            messages.success(request, _('تم إضافة الوحدة بنجاح'))
            return redirect('buildings:unit_detail', unit_id=unit.id)
    else:
        form = UnitForm()
    
    return render(request, 'buildings/unit_form.html', {
        'form': form,
        'title': _('إضافة وحدة جديدة')
    })


@login_required
def unit_edit(request, unit_id):
    """تعديل الوحدة"""
    unit = get_object_or_404(Unit, id=unit_id)
    
    if request.method == 'POST':
        form = UnitForm(request.POST, instance=unit)
        if form.is_valid():
            form.save()
            messages.success(request, _('تم تحديث الوحدة بنجاح'))
            return redirect('buildings:unit_detail', unit_id=unit.id)
    else:
        form = UnitForm(instance=unit)
    
    return render(request, 'buildings/unit_form.html', {
        'form': form,
        'unit': unit,
        'title': _('تعديل الوحدة')
    })


@login_required
def floor_create(request, building_id):
    """إضافة طابق جديد"""
    building = get_object_or_404(Building, id=building_id)
    
    if request.method == 'POST':
        form = FloorForm(request.POST)
        if form.is_valid():
            floor = form.save(commit=False)
            floor.building = building
            floor.save()
            messages.success(request, _('تم إضافة الطابق بنجاح'))
            return redirect('buildings:detail', building_id=building.id)
    else:
        form = FloorForm()
    
    return render(request, 'buildings/floor_form.html', {
        'form': form,
        'building': building,
        'title': _('إضافة طابق جديد')
    })

