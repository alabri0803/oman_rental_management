from django.urls import path
from . import views

app_name = 'tenants'

urlpatterns = [
    # المستأجرون
    path('', views.tenant_list, name='list'),
    path('<int:tenant_id>/', views.tenant_detail, name='detail'),
    path('create/', views.tenant_create, name='create'),
    path('<int:tenant_id>/edit/', views.tenant_edit, name='edit'),
    path('<int:tenant_id>/delete/', views.tenant_delete, name='delete'),
    path('<int:tenant_id>/deactivate/', views.tenant_deactivate, name='deactivate'),
    path('<int:tenant_id>/activate/', views.tenant_activate, name='activate'),
    
    # الوثائق
    path('<int:tenant_id>/documents/upload/', views.document_upload, name='document_upload'),
    path('<int:tenant_id>/documents/<int:document_id>/delete/', views.document_delete, name='document_delete'),
    
    # AJAX
    path('search/', views.tenant_search_ajax, name='search_ajax'),
    
    # الإحصائيات
    path('statistics/', views.tenant_statistics, name='statistics'),
]

