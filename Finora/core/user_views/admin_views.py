from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
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
import secrets
import string


@login_required
def admin_dashboard(request):
    """Admin dashboard with overview statistics"""
    try:
        user_data = UserData.objects.get(user=request.user)
        if user_data.role != 'Admin':
            messages.error(request, "Access denied. Admin privileges required.")
            return redirect('core:dashboard')
        
        company = user_data.company
    except UserData.DoesNotExist:
        messages.error(request, "User data not found. Please contact administrator.")
        return redirect('core:dashboard')
    
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
    
    # Get approval rules count
    total_rules = ApprovalRules.objects.filter(
        employee__company=company
    ).count()
    
    context = {
        'user_data': user_data,
        'total_employees': total_employees,
        'total_managers': total_managers,
        'total_expenses': total_expenses,
        'pending_approvals': pending_approvals,
        'total_rules': total_rules,
        'recent_users': recent_users,
        'recent_expenses': recent_expenses,
    }
    
    return render(request, 'core/admin_dashboard.html', context)


@login_required
def admin_users(request):
    """User management page"""
    try:
        user_data = UserData.objects.get(user=request.user)
        if user_data.role != 'Admin':
            messages.error(request, "Access denied. Admin privileges required.")
            return redirect('core:dashboard')
        
        company = user_data.company
    except UserData.DoesNotExist:
        messages.error(request, "User data not found. Please contact administrator.")
        return redirect('core:dashboard')
    
    # Get all users in the company (excluding other admins)
    all_users = UserData.objects.filter(
        company=company
    ).exclude(role='Admin').order_by('role', 'name')
    
    # Get managers for dropdown (Admin and Manager roles)
    managers = UserData.objects.filter(
        company=company, 
        role__in=['Admin', 'Manager']
    ).order_by('name')
    
    context = {
        'user_data': user_data,
        'all_users': all_users,
        'managers': managers,
    }
    
    return render(request, 'core/admin_users.html', context)


@login_required
def admin_approval_rules(request):
    """Approval rules configuration page"""
    try:
        user_data = UserData.objects.get(user=request.user)
        if user_data.role != 'Admin':
            messages.error(request, "Access denied. Admin privileges required.")
            return redirect('core:dashboard')
        
        company = user_data.company
    except UserData.DoesNotExist:
        messages.error(request, "User data not found. Please contact administrator.")
        return redirect('core:dashboard')
    
    # Get all non-admin users and managers
    all_users = UserData.objects.filter(
        company=company
    ).exclude(role='Admin').order_by('id')
    
    managers = UserData.objects.filter(
        company=company, 
        role__in=['Admin', 'Manager']
    ).order_by('id')
    
    # Get existing approval rules
    approval_rules = ApprovalRules.objects.filter(
        employee__company=company
    ).prefetch_related('approvers')
    
    context = {
        'user_data': user_data,
        'all_users': all_users,
        'managers': managers,
        'approval_rules': approval_rules,
    }
    
    return render(request, 'core/admin_approval_rules.html', context)


def generate_password(length=12):
    """Generate a secure random password"""
    characters = string.ascii_letters + string.digits + "!@#$%^&*"
    password = ''.join(secrets.choice(characters) for _ in range(length))
    return password


@login_required
@require_http_methods(["POST"])
def add_user(request):
    """Add new user to the company"""
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
        
        # Validate data
        if not all([username, email, role]):
            return JsonResponse({'success': False, 'error': 'All fields are required'})
        
        # Check if username/email already exists
        if User.objects.filter(username=username).exists():
            return JsonResponse({'success': False, 'error': 'Username already exists'})
        
        if User.objects.filter(email=email).exists():
            return JsonResponse({'success': False, 'error': 'Email already exists'})
        
        # Generate random password
        temp_password = generate_password()
        
        # Create Django User
        user = User.objects.create_user(
            username=username,
            email=email,
            password=temp_password
        )
        
        # Get manager
        manager = None
        if manager_id:
            try:
                manager = UserData.objects.get(id=manager_id, company=company)
                # Ensure the manager can manage this role
                if role == 'Admin' and manager.role != 'Admin':
                    return JsonResponse({'success': False, 'error': 'Only admins can assign admin roles'})
            except UserData.DoesNotExist:
                pass
        
        # Create UserData
        user_data_obj = UserData.objects.create(
            user=user,
            role=role,
            company=company,
            manager=manager
        )
        
        # Auto-create default approval rule for employees/managers
        if role in ['Employee', 'Manager']:
            ApprovalRules.objects.create(
                employee=user_data_obj,
                description=f"Default approval rule for {role}",
                manager=manager if role == 'Employee' else None,
                manager_approval=role == 'Employee',
                approval_sequence=False,
                min_approval_percentage=51
            )
        
        # Send credentials email
        send_welcome_email(user, temp_password, request)
        
        return JsonResponse({
            'success': True, 
            'message': f'User created successfully. Credentials sent to {email}'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
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
        
        # Generate new password
        new_password = generate_password()
        target_user.set_password(new_password)
        target_user.save()
        
        # Send credentials email
        send_new_password_email(target_user, new_password, request)
        
        return JsonResponse({
            'success': True, 
            'message': f'New password generated and sent to {target_user.email}'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_http_methods(["POST"])
def delete_user(request, user_id):
    """Delete user from company"""
    try:
        user_data = UserData.objects.get(user=request.user)
        if user_data.role != 'Admin':
            return JsonResponse({'success': False, 'error': 'Access denied'})
        
        # Get target user
        target_user_data = get_object_or_404(UserData, id=user_id, company=user_data.company)
        
        # Prevent self-deletion
        if target_user_data.id == user_data.id:
            return JsonResponse({'success': False, 'error': 'You cannot delete yourself'})
        
        target_user = target_user_data.user
        
        # Delete associated approval rules first
        ApprovalRules.objects.filter(employee=target_user_data).delete()
        
        # Delete user (this will cascade to UserData)
        target_user.delete()
        
        return JsonResponse({'success': True, 'message': 'User deleted successfully'})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
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
        
        # Handle approvers
        approver_ids = request.POST.getlist('approver_ids[]')
        
        # Clear existing approvers
        rules.approvers.clear()
        
        # Add new approvers
        for approver_id in approver_ids:
            if approver_id:
                try:
                    approver = UserData.objects.get(id=approver_id, company=user_data.company)
                    rules.approvers.add(approver)
                except UserData.DoesNotExist:
                    pass
        
        return JsonResponse({'success': True, 'message': 'Approval rules saved successfully'})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
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
                'manager_id': rules.manager.id if rules.manager else None,
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


@login_required
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


def send_welcome_email(user, password, request):
    """Send welcome email with credentials"""
    try:
        reset_url = f"{request.scheme}://{request.get_host()}/user/login/"
        
        send_mail(
            subject='Welcome to Finora Expense Management',
            message=f'''
            Welcome to Finora Expense Management System!
            
            Your account has been created with the following credentials:
            
            Username: {user.username}
            Password: {password}
            Login URL: {reset_url}
            
            Please change your password after your first login.
            
            Best regards,
            Finora Team
            ''',
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@finora.com'),
            recipient_list=[user.email],
            fail_silently=False,
        )
    except Exception as e:
        print(f"Email sending failed: {e}")


def send_new_password_email(user, password, request):
    """Send new password email"""
    try:
        reset_url = f"{request.scheme}://{request.get_host()}/user/login/"
        
        send_mail(
            subject='Your New Password - Finora Expense Management',
            message=f'''
            Hello {user.username},
            
            Your password has been reset by an administrator.
            
            New Password: {password}
            Login URL: {reset_url}
            
            Please change your password after your login.
            
            Best regards,
            Finora Team
            ''',
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@finora.com'),
            recipient_list=[user.email],
            fail_silently=False,
        )
    except Exception as e:
        print(f"Email sending failed: {e}")
