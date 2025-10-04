from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import json

from ..models import Expense, ExpenseApproval
from user_app.models import UserData


@login_required
def manager_dashboard(request):
    """Manager dashboard showing expenses awaiting their approval"""
    try:
        user_data = UserData.objects.get(user=request.user)
        
        # Check if user is a manager
        if user_data.role != 'Manager':
            messages.error(request, 'Access denied. This page is for managers only.')
            return redirect('core:dashboard')
        
        # Get expenses that need this manager's approval
        # We'll find expenses where:
        # 1. The manager has approval records for expenses
        # 2. The approval status is Pending
        pending_approvals = ExpenseApproval.objects.filter(
            approver=user_data,
            status='Pending'
        ).select_related('expense', 'expense__employee').order_by('-created_at')
        
        # Get total approvals for this manager (for stats)
        total_approvals = ExpenseApproval.objects.filter(approver=user_data).count()
        approved_count = ExpenseApproval.objects.filter(approver=user_data, status='Approved').count()
        rejected_count = ExpenseApproval.objects.filter(approver=user_data, status='Rejected').count()
        pending_count = pending_approvals.count()
        
        # Get recent expenses awaiting approval (for quick view)
        recent_expenses = []
        for approval in pending_approvals[:10]:  # Limit to 10 most recent
            recent_expenses.append(approval.expense)
        
        context = {
            'user_data': user_data,
            'pending_approvals': pending_approvals,
            'recent_expenses': recent_expenses,
            'total_approvals': total_approvals,
            'approved_count': approved_count,
            'rejected_count': rejected_count,
            'pending_count': pending_count,
        }
        
        return render(request, 'core/manager_dashboard.html', context)
        
    except UserData.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('user_app:login')


@login_required
@csrf_exempt
def approve_expense(request, expense_id):
    """Handle expense approval/rejection via AJAX"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method'})
    
    try:
        user_data = UserData.objects.get(user=request.user)
        
        # Check if user is a manager
        if user_data.role != 'Manager':
            return JsonResponse({'success': False, 'message': 'Access denied'})
        
        # Get the expense and approval record
        expense = get_object_or_404(Expense, id=expense_id)
        approval = get_object_or_404(
            ExpenseApproval, 
            expense=expense, 
            approver=user_data,
            status='Pending'
        )
        
        # Get approval data
        data = json.loads(request.body)
        action = data.get('action')  # 'approve' or 'reject'
        remarks = data.get('remarks', '')
        
        if action not in ['approve', 'reject']:
            return JsonResponse({'success': False, 'message': 'Invalid action'})
        
        # Update approval status
        new_status = 'Approved' if action == 'approve' else 'Rejected'
        approval.status = new_status
        if remarks:
            approval.expense.remarks = f"{approval.expense.remarks}\nManager Note: {remarks}".strip()
            approval.expense.save()
        approval.save()
        
        # Update the main expense status based on all approvals
        expense.update_status_from_approvals()
        
        action_text = 'approved' if action == 'approve' else 'rejected'
        return JsonResponse({
            'success': True, 
            'message': f'Expense {action_text} successfully!',
            'expense_id': expense.id,
            'new_status': new_status
        })
        
    except UserData.DoesNotExist:
        return JsonResponse({'status': False, 'message': 'User profile not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})


@login_required
def get_expense_for_approval(request, expense_id):
    """Get expense details for approval modal"""
    try:
        user_data = UserData.objects.get(user=request.user)
        expense = get_object_or_404(Expense, id=expense_id)
        
        # Check if this manager needs to approve this expense
        approval = get_object_or_404(
            ExpenseApproval, 
            expense=expense, 
            approver=user_data
        )
        
        # Get all approvals for this expense to show approval chain
        all_approvals = ExpenseApproval.objects.filter(expense=expense).select_related('approver')
        
        expense_data = {
            'id': expense.id,
            'description': expense.description,
            'date': expense.date.strftime('%Y-%m-%d'),
            'category': expense.category,
            'amount': float(expense.amount),
            'currency': expense.currency,
            'status': expense.status,
            'remarks': expense.remarks,
            'employee': {
                'name': expense.employee.name,
                'email': expense.employee.email,
                'department': expense.employee.company.name
            },
            'created_at': expense.created_at.strftime('%Y-%m-%d %H:%M'),
            'updated_at': expense.updated_at.strftime('%Y-%m-%d %H:%M'),
            'has_receipt': bool(expense.receipt),
            'receipt_url': expense.receipt.url if expense.receipt else None,
            'approvals': [
                {
                    'approver_name': approval.approver.name,
                    'approver_email': approval.approver.email,
                    'status': approval.status,
                    'created_at': approval.created_at.strftime('%Y-%m-%d %H:%M')
                } for approval in all_approvals
            ],
            'current_approval_id': approval.id
        }
        
        return JsonResponse({'success': True, 'expense': expense_data})
        
    except UserData.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'User profile not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})


@login_required
def manager_expense_history(request):
    """Show all expenses manager has processed (approved/rejected)"""
    try:
        user_data = UserData.objects.get(user=request.user)
        
        if user_data.role != 'Manager':
            messages.error(request, 'Access denied. This page is for managers only.')
            return redirect('core:dashboard')
        
        # Get all approvals processed by this manager
        processed_approvals = ExpenseApproval.objects.filter(
            approver=user_data
        ).exclude(status='Pending').select_related('expense', 'expense__employee').order_by('-updated_at')
        
        context = {
            'user_data': user_data,
            'processed_approvals': processed_approvals,
        }
        
        return render(request, 'core/manager_history.html', context)
        
    except UserData.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('user_app:login')
