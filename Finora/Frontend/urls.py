from django.urls import path
from . import views
from . import admin_views

ADMIN_PANEL_PREFIX = 'expense-admin/'

urlpatterns = [
    path('', views.index, name='index'),
    
    # Admin URLs
    path(f'{ADMIN_PANEL_PREFIX}dashboard/', admin_views.admin_dashboard, name='admin_dashboard'),
    path(f'{ADMIN_PANEL_PREFIX}users/', admin_views.admin_users, name='admin_users'),
    path(f'{ADMIN_PANEL_PREFIX}approval-rules/', admin_views.admin_approval_rules, name='admin_approval_rules'),
    path(f'{ADMIN_PANEL_PREFIX}expenses/', admin_views.admin_expenses, name='admin_expenses'),
    path(f'{ADMIN_PANEL_PREFIX}approvals/', admin_views.admin_approvals, name='admin_approvals'),
    path(f'{ADMIN_PANEL_PREFIX}reports/', admin_views.admin_reports, name='admin_reports'),
    
    # Admin API endpoints
    path(f'{ADMIN_PANEL_PREFIX}add-user/', admin_views.add_user, name='add_user'),
    path(f'{ADMIN_PANEL_PREFIX}send-password/<int:user_id>/', admin_views.send_password_reset, name='send_password'),
    path(f'{ADMIN_PANEL_PREFIX}delete-user/<int:user_id>/', admin_views.delete_user, name='delete_user'),
    path(f'{ADMIN_PANEL_PREFIX}save-approval-rules/', admin_views.save_approval_rules, name='save_approval_rules'),
    path(f'{ADMIN_PANEL_PREFIX}get-user-rules/<int:user_id>/', admin_views.get_user_rules, name='get_user_rules'),
    path(f'{ADMIN_PANEL_PREFIX}get-user-manager/<int:user_id>/', admin_views.get_user_manager, name='get_user_manager'),
    path(f'{ADMIN_PANEL_PREFIX}delete-rule/<int:rule_id>/', admin_views.delete_rule, name='delete_rule'),
]
