from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import json
import os

from ..models import Expense
from user_app.models import UserData


@login_required
def employee_dashboard(request):
    """Employee dashboard showing their expenses and options to add/upload expenses"""
    try:
        user_data = UserData.objects.get(user=request.user)
        
        # Check if user is an employee
        if user_data.role != 'Employee':
            messages.error(request, 'Access denied. This page is for employees only.')
            return redirect('core:dashboard')
        
        # Get all expenses for this employee
        expenses = Expense.objects.filter(employee=user_data).order_by('-created_at')
        
        context = {
            'user_data': user_data,
            'expenses': expenses,
            'total_expenses': expenses.count(),
            'pending_expenses': expenses.filter(status='Pending').count(),
            'approved_expenses': expenses.filter(status='Approved').count(),
            'rejected_expenses': expenses.filter(status='Rejected').count(),
        }
        
        return render(request, 'core/employee_dashboard.html', context)
        
    except UserData.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('user_app:login')


@login_required
@csrf_exempt
def add_expense(request):
    """Handle adding new expense via AJAX"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method'})
    
    try:
        user_data = UserData.objects.get(user=request.user)
        
        # Check if user is an employee
        if user_data.role != 'Employee':
            return JsonResponse({'success': False, 'message': 'Access denied'})
        
        # Get form data
        data = json.loads(request.body)
        
        # Create new expense
        expense = Expense.objects.create(
            employee=user_data,
            description=data.get('description', ''),
            date=data.get('date', timezone.now().date()),
            category=data.get('category', 'Other'),
            amount=data.get('amount', 0),
            currency=data.get('currency', 'INR'),
            remarks=data.get('remarks', ''),
            status='Draft'
        )
        
        return JsonResponse({
            'success': True, 
            'message': 'Expense added successfully!',
            'expense_id': expense.id
        })
        
    except UserData.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'User profile not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})


@login_required
@csrf_exempt
def upload_expense(request):
    """Handle uploading expense receipt/image"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method'})
    
    try:
        user_data = UserData.objects.get(user=request.user)
        
        # Check if user is an employee
        if user_data.role != 'Employee':
            return JsonResponse({'success': False, 'message': 'Access denied'})
        
        # Get uploaded file
        if 'receipt_file' not in request.FILES:
            return JsonResponse({'success': False, 'message': 'No file uploaded'})
        
        file = request.FILES['receipt_file']
        
        # Validate file type
        allowed_extensions = ['.pdf', '.jpg', '.jpeg', '.png']
        file_extension = os.path.splitext(file.name)[1].lower()
        
        if file_extension not in allowed_extensions:
            return JsonResponse({
                'success': False, 
                'message': 'Invalid file type. Please upload PDF, JPG, JPEG, or PNG files only.'
            })
        
        # Create a temporary expense record for the uploaded file
        expense = Expense.objects.create(
            employee=user_data,
            description=f"Uploaded receipt: {file.name}",
            date=timezone.now().date(),
            category='Other',
            amount=0,  # Will be processed later
            currency='INR',
            remarks='Receipt uploaded for processing',
            status='Draft',
            receipt=file
        )
        
        return JsonResponse({
            'success': True, 
            'message': 'Receipt uploaded successfully! It will be processed soon.',
            'expense_id': expense.id,
            'filename': file.name
        })
        
    except UserData.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'User profile not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})


@login_required
def get_expense_details(request, expense_id):
    """Get expense details for modal display"""
    try:
        user_data = UserData.objects.get(user=request.user)
        expense = get_object_or_404(Expense, id=expense_id, employee=user_data)
        
        expense_data = {
            'id': expense.id,
            'description': expense.description,
            'date': expense.date.strftime('%Y-%m-%d'),
            'category': expense.category,
            'amount': float(expense.amount),
            'currency': expense.currency,
            'status': expense.status,
            'remarks': expense.remarks,
            'created_at': expense.created_at.strftime('%Y-%m-%d %H:%M'),
            'updated_at': expense.updated_at.strftime('%Y-%m-%d %H:%M'),
            'has_receipt': bool(expense.receipt),
            'receipt_url': expense.receipt.url if expense.receipt else None,
        }
        
        return JsonResponse({'success': True, 'expense': expense_data})
        
    except UserData.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'User profile not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})
