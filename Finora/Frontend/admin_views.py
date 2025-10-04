from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Count
from user_app.models import UserData, CompanyData, PasswordResetToken
from core.models import Expense, ExpenseApproval, ApprovalRules
from django.utils import timezone
import json
import uuid


# @login_required
def admin_dashboard(request):
    """Admin dashboard with overview statistics"""
    # Get current user's company
    try:
        user_data = UserData.objects.get(user=request.user)
        company = user_data.company
    except UserData.DoesNotExist:
        messages.error(request, "User data not found. Please contact administrator.")
        return redirect('index')
    
    # Check if user is admin
    if user_data.role != 'Admin':
        messages.error(request, "Access denied. Admin privileges required.")
        return redirect('index')
    
    # Get statistics
    total_employees = UserData.objects.filter(company=company).count()
    total_managers = UserData.objects.filter(company=company, role='Manager').count()
    total_expenses = Expense.objects.filter(employee__company=company).count()
    pending_approvals = ExpenseApproval.objects.filter(
        expense__employee__company=company,
        status='Pending'
    ).count()
    
    # Get recent users (last 10)
    recent_users = UserData.objects.filter(company=company).order_by('-created_at')[:10]
    
    # Get recent expenses (last 10)
    recent_expenses = Expense.objects.filter(
        employee__company=company
    ).order_by('-created_at')[:10]
    
    context = {
        'total_employees': total_employees,
        'total_managers': total_managers,
        'total_expenses': total_expenses,
        'pending_approvals': pending_approvals,
        'recent_users': recent_users,
        'recent_expenses': recent_expenses,
    }
    
    return render(request, 'admin_dashboard.html', context)


# @login_required
def admin_users(request):
    """User management page"""
    try:
        user_data = UserData.objects.get(user=request.user)
        company = user_data.company
    except UserData.DoesNotExist:
        messages.error(request, "User data not found. Please contact administrator.")
        return redirect('index')
    
    if user_data.role != 'Admin':
        messages.error(request, "Access denied. Admin privileges required.")
        return redirect('index')
    
    # Get all users in the company
    all_users = UserData.objects.filter(company=company).order_by('-created_at')
    
    # Get managers for dropdown
    managers = UserData.objects.filter(company=company, role__in=['Admin', 'Manager'])
    
    context = {
        'all_users': all_users,
        'managers': managers,
    }
    
    return render(request, 'admin_users.html', context)


# @login_required
def admin_approval_rules(request):
    """Approval rules configuration page"""
    try:
        user_data = UserData.objects.get(user=request.user)
        company = user_data.company
    except UserData.DoesNotExist:
        messages.error(request, "User data not found. Please contact administrator.")
        return redirect('index')
    
    if user_data.role != 'Admin':
        messages.error(request, "Access denied. Admin privileges required.")
        return redirect('index')
    
    # Get all users and managers
    all_users = UserData.objects.filter(company=company).order_by('name')
    managers = UserData.objects.filter(company=company, role__in=['Admin', 'Manager']).order_by('name')
    
    context = {
        'all_users': all_users,
        'managers': managers,
    }
    
    return render(request, 'admin_approval_rules.html', context)


# @login_required
@require_http_methods(["POST"])
def add_user(request):
    """Add new user"""
    try:
        user_data = UserData.objects.get(user=request.user)
        if user_data.role != 'Admin':
            return JsonResponse({'success': False, 'error': 'Access denied'})
        
        company = user_data.company
        
        # Get form data
        username = request.POST.get('username')
        email = request.POST.get('email')
        role = request.POST.get('role')
        manager_id = request.POST.get('manager')
        password = request.POST.get('password')
        
        # Create Django User
        if User.objects.filter(username=username).exists():
            return JsonResponse({'success': False, 'error': 'Username already exists'})
        
        if User.objects.filter(email=email).exists():
            return JsonResponse({'success': False, 'error': 'Email already exists'})
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        
        # Create UserData
        manager = None
        if manager_id:
            try:
                manager = UserData.objects.get(id=manager_id, company=company)
            except UserData.DoesNotExist:
                pass
        
        user_data_obj = UserData.objects.create(
            user=user,
            role=role,
            company=company,
            manager=manager
        )
        
        return JsonResponse({'success': True, 'message': 'User created successfully'})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# @login_required
@require_http_methods(["POST"])
def send_password_reset(request, user_id):
    """Send password reset email to user"""
    try:
        user_data = UserData.objects.get(user=request.user)
        if user_data.role != 'Admin':
            return JsonResponse({'success': False, 'error': 'Access denied'})
        
        # Get target user
        target_user_data = get_object_or_404(UserData, id=user_id, company=user_data.company)
        target_user = target_user_data.user
        
        # Create password reset token
        token = PasswordResetToken.objects.create(user=target_user)
        
        # Send email
        reset_url = f"{request.scheme}://{request.get_host()}/user/reset-password/{token.token}/"
        
        send_mail(
            subject='Password Reset - Finora Expense Management',
            message=f'''
            Hello {target_user.username},
            
            A password reset has been requested for your account.
            Please click the link below to reset your password:
            
            {reset_url}
            
            This link will expire in 24 hours.
            
            If you did not request this password reset, please ignore this email.
            
            Best regards,
            Finora Team
            ''',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[target_user.email],
            fail_silently=False,
        )
        
        return JsonResponse({'success': True, 'message': 'Password reset email sent'})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# @login_required
@require_http_methods(["POST"])
def delete_user(request, user_id):
    """Delete user"""
    try:
        user_data = UserData.objects.get(user=request.user)
        if user_data.role != 'Admin':
            return JsonResponse({'success': False, 'error': 'Access denied'})
        
        # Get target user
        target_user_data = get_object_or_404(UserData, id=user_id, company=user_data.company)
        target_user = target_user_data.user
        
        # Delete user (this will cascade to UserData)
        target_user.delete()
        
        return JsonResponse({'success': True, 'message': 'User deleted successfully'})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# @login_required
@require_http_methods(["POST"])
def save_approval_rules(request):
    """Save approval rules for a user"""
    try:
        user_data = UserData.objects.get(user=request.user)
        if user_data.role != 'Admin':
            return JsonResponse({'success': False, 'error': 'Access denied'})
        
        # Get form data
        user_id = request.POST.get('user_id')
        description = request.POST.get('description')
        manager_id = request.POST.get('manager')
        manager_approval = request.POST.get('manager_approval') == 'on'
        approval_sequence = request.POST.get('approval_sequence') == 'on'
        min_approval_percentage = int(request.POST.get('min_approval_percentage', 51))
        
        # Get target user
        target_user = get_object_or_404(UserData, id=user_id, company=user_data.company)
        
        # Get manager
        manager = None
        if manager_id:
            manager = get_object_or_404(UserData, id=manager_id, company=user_data.company)
        
        # Create or update approval rules
        rules, created = ApprovalRules.objects.get_or_create(
            employee=target_user,
            defaults={
                'description': description,
                'manager': manager,
                'manager_approval': manager_approval,
                'approval_sequence': approval_sequence,
                'min_approval_percentage': min_approval_percentage,
            }
        )
        
        if not created:
            rules.description = description
            rules.manager = manager
            rules.manager_approval = manager_approval
            rules.approval_sequence = approval_sequence
            rules.min_approval_percentage = min_approval_percentage
            rules.save()
        
        # Handle approvers (simplified - in real implementation, you'd handle multiple approvers)
        approver_ids = request.POST.getlist('approver_ids')
        approver_required = request.POST.getlist('approver_required')
        
        # Clear existing approvers
        rules.approvers.clear()
        
        # Add new approvers
        for i, approver_id in enumerate(approver_ids):
            if approver_id:
                try:
                    approver = UserData.objects.get(id=approver_id, company=user_data.company)
                    rules.approvers.add(approver)
                except UserData.DoesNotExist:
                    pass
        
        return JsonResponse({'success': True, 'message': 'Approval rules saved successfully'})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# @login_required
def get_user_rules(request, user_id):
    """Get approval rules for a specific user"""
    try:
        user_data = UserData.objects.get(user=request.user)
        if user_data.role != 'Admin':
            return JsonResponse({'success': False, 'error': 'Access denied'})
        
        # Get target user
        target_user = get_object_or_404(UserData, id=user_id, company=user_data.company)
        
        # Get approval rules
        rules = ApprovalRules.objects.filter(employee=target_user).first()
        
        if rules:
            rules_data = {
                'id': rules.id,
                'description': rules.description,
                'manager_name': rules.manager.name if rules.manager else 'No Manager',
                'manager_approval': rules.manager_approval,
                'approvers': [{'id': a.id, 'name': a.name} for a in rules.approvers.all()],
                'approval_sequence': rules.approval_sequence,
                'min_approval_percentage': rules.min_approval_percentage,
            }
            return JsonResponse({'success': True, 'rules': rules_data})
        else:
            return JsonResponse({'success': True, 'rules': None})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# @login_required
def get_user_manager(request, user_id):
    """Get manager for a specific user"""
    try:
        user_data = UserData.objects.get(user=request.user)
        if user_data.role != 'Admin':
            return JsonResponse({'success': False, 'error': 'Access denied'})
        
        # Get target user
        target_user = get_object_or_404(UserData, id=user_id, company=user_data.company)
        
        return JsonResponse({
            'success': True,
            'manager_id': target_user.manager.id if target_user.manager else None
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# @login_required
@require_http_methods(["POST"])
def delete_rule(request, rule_id):
    """Delete approval rule"""
    try:
        user_data = UserData.objects.get(user=request.user)
        if user_data.role != 'Admin':
            return JsonResponse({'success': False, 'error': 'Access denied'})
        
        # Get rule
        rule = get_object_or_404(ApprovalRules, id=rule_id, employee__company=user_data.company)
        rule.delete()
        
        return JsonResponse({'success': True, 'message': 'Rule deleted successfully'})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# @login_required
def admin_expenses(request):
    """Expense management page"""
    try:
        user_data = UserData.objects.get(user=request.user)
        company = user_data.company
    except UserData.DoesNotExist:
        messages.error(request, "User data not found. Please contact administrator.")
        return redirect('index')
    
    if user_data.role != 'Admin':
        messages.error(request, "Access denied. Admin privileges required.")
        return redirect('index')
    
    # Get all expenses in the company
    expenses = Expense.objects.filter(employee__company=company).order_by('-created_at')
    
    context = {
        'expenses': expenses,
    }
    
    return render(request, 'admin_expenses.html', context)


# @login_required
def admin_approvals(request):
    """Approvals management page"""
    try:
        user_data = UserData.objects.get(user=request.user)
        company = user_data.company
    except UserData.DoesNotExist:
        messages.error(request, "User data not found. Please contact administrator.")
        return redirect('index')
    
    if user_data.role != 'Admin':
        messages.error(request, "Access denied. Admin privileges required.")
        return redirect('index')
    
    # Get all pending approvals
    approvals = ExpenseApproval.objects.filter(
        expense__employee__company=company,
        status='Pending'
    ).order_by('-created_at')
    
    context = {
        'approvals': approvals,
    }
    
    return render(request, 'admin_approvals.html', context)


# @login_required
def admin_reports(request):
    """Reports page"""
    try:
        user_data = UserData.objects.get(user=request.user)
        company = user_data.company
    except UserData.DoesNotExist:
        messages.error(request, "User data not found. Please contact administrator.")
        return redirect('index')
    
    if user_data.role != 'Admin':
        messages.error(request, "Access denied. Admin privileges required.")
        return redirect('index')
    
    # Get report data
    expenses_by_category = Expense.objects.filter(
        employee__company=company
    ).values('category').annotate(count=Count('id')).order_by('-count')
    
    expenses_by_status = Expense.objects.filter(
        employee__company=company
    ).values('status').annotate(count=Count('id')).order_by('-count')
    
    context = {
        'expenses_by_category': expenses_by_category,
        'expenses_by_status': expenses_by_status,
    }
    
    return render(request, 'admin_reports.html', context)
