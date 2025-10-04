from django.contrib import admin
from .models import Expense, ExpenseApproval, ApprovalRules

# Register your models here.

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('employee', 'description', 'date', 'category', 'amount', 'currency', 'status', 'paid_by', 'created_at')
    list_filter = ('status', 'category', 'date', 'created_at', 'employee__company')
    search_fields = ('employee__name', 'employee__email', 'description')
    list_select_related = ('employee', 'paid_by')
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Expense Details', {
            'fields': ('employee', 'description', 'date', 'category', 'amount', 'currency')
        }),
        ('Payment & Status', {
            'fields': ('paid_by', 'status', 'receipt')
        }),
        ('Additional Info', {
            'fields': ('remarks',),
            'classes': ('collapse',)
        }),
    )

@admin.register(ExpenseApproval)
class ExpenseApprovalAdmin(admin.ModelAdmin):
    list_display = ('expense', 'approver', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('expense__employee__name', 'approver__name', 'approver__email')
    list_select_related = ('expense', 'approver')

@admin.register(ApprovalRules)
class ApprovalRulesAdmin(admin.ModelAdmin):
    list_display = ('employee', 'manager', 'manager_approval', 'approval_sequence', 'min_approval_percentage')
    list_filter = ('manager_approval', 'approval_sequence')
    search_fields = ('employee__name', 'manager__name', 'description')
    filter_horizontal = ('approvers',)
    list_select_related = ('employee', 'manager')
