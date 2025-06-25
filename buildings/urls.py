from django.urls import path
from . import views

app_name = 'buildings'

urlpatterns = [
    # المباني
    path('', views.building_list, name='list'),
    path('<int:building_id>/', views.building_detail, name='detail'),
    path('create/', views.building_create, name='create'),
    path('<int:building_id>/edit/', views.building_edit, name='edit'),
    path('<int:building_id>/delete/', views.building_delete, name='delete'),
    
    # الطوابق
    path('<int:building_id>/floors/create/', views.floor_create, name='floor_create'),
    
    # الوحدات
    path('units/', views.unit_list, name='unit_list'),
    path('units/<int:unit_id>/', views.unit_detail, name='unit_detail'),
    path('units/create/', views.unit_create, name='unit_create'),
    path('units/<int:unit_id>/edit/', views.unit_edit, name='unit_edit'),
]

