from django.urls import path
from . import views
from . import views  
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse

app_name= 'adminpanel'

urlpatterns = [

    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('users/', views.get_all_users, name='admin_users'),
    path('users/<int:user_id>/', views.delete_user, name='admin_delete_user'),
    path('contributions/<int:contrib_id>/', views.update_contribution, name='admin_update_contrib'),
    path('contributions/<int:contrib_id>/delete/', views.delete_contribution, name='admin_delete_contrib'),
    path('contributions/<int:contrib_id>/approve/<str:csv_type>/', views.approve_contribution, name='admin_approve_contrib'),
    path('logout/', views.admin_logout_view, name='admin_logout'),
]
