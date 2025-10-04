from django.urls import include, path
from . import views
from .user_views import emp_views, mang_views, admin_views

app_name = "core"

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Employee URLs
    path('employee/dashboard/', emp_views.employee_dashboard, name='employee_dashboard'),
    path('employee/add-expense/', emp_views.add_expense, name='add_expense'),
    path('employee/upload-expense/', emp_views.upload_expense, name='upload_expense'),
    path('employee/expense/<int:expense_id>/', emp_views.get_expense_details, name='expense_details'),
    
    # Manager URLs
    path('manager/dashboard/', mang_views.manager_dashboard, name='manager_dashboard'),
    path('manager/history/', mang_views.manager_expense_history, name='manager_history'),
    path('manager/approve/<int:expense_id>/', mang_views.approve_expense, name='approve_expense'),
    path('manager/expense/<int:expense_id>/', mang_views.get_expense_for_approval, name='expense_approval'),
    
    # Admin URLs
    path('admin/dashboard/', admin_views.admin_dashboard, name='admin_dashboard'),
    path('admin/users/', admin_views.admin_users, name='admin_users'),
    path('admin/approval-rules/', admin_views.admin_approval_rules, name='admin_approval_rules'),
    
    # Admin API endpoints
    path('admin/add-user/', admin_views.add_user, name='admin_add_user'),
    path('admin/send-password/<int:user_id>/', admin_views.send_password_reset, name='admin_send_password'),
    path('admin/delete-user/<int:user_id>/', admin_views.delete_user, name='admin_delete_user'),
    path('admin/save-approval-rules/', admin_views.save_approval_rules, name='admin_save_approval_rules'),
    path('admin/get-user-rules/<int:user_id>/', admin_views.get_user_rules, name='admin_get_user_rules'),
    path('admin/delete-rule/<int:rule_id>/', admin_views.delete_rule, name='admin_delete_rule'),
]