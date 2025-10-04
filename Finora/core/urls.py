from django.urls import include, path
from . import views
from .user_views import emp_views

app_name = "core"

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('employee/dashboard/', emp_views.employee_dashboard, name='employee_dashboard'),
    path('employee/add-expense/', emp_views.add_expense, name='add_expense'),
    path('employee/upload-expense/', emp_views.upload_expense, name='upload_expense'),
    path('employee/expense/<int:expense_id>/', emp_views.get_expense_details, name='expense_details'),
]