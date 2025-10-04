from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.http import HttpResponse
from .models import UserData, CompanyData, PasswordResetToken
import uuid

# Create your views here.

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful!')
            return redirect('core:dashboard')  # Redirect to dashboard
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'user_app/login.html')

def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        company_name = request.POST.get('company_name')
        country = request.POST.get('country')
        currency = request.POST.get('currency')
        role = request.POST.get('role', 'Admin')
        
        # Validation
        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'user_app/signup.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'user_app/signup.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return render(request, 'user_app/signup.html')
        
        try:
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            
            # Create or get company
            company, created = CompanyData.objects.get_or_create(
                name=company_name,
                defaults={'country': country, 'currency': currency}
            )
            
            # Create user data
            user_data = UserData.objects.create(
                user=user,
                company=company,
                role=role
            )
            
            messages.success(request, 'Account created successfully! Please login.')
            return redirect('user_app:login')
            
        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}')
    
    return render(request, 'user_app/signup.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('user_app:login')

def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        
        try:
            user = User.objects.get(email=email)
            
            # Create password reset token
            reset_token = PasswordResetToken.objects.create(user=user)
            
            # Send email
            reset_url = f"{request.scheme}://{request.get_host()}/user/reset-password/{reset_token.token}/"
            
            subject = 'Password Reset Request'
            message = f'''
            Hello {user.username},
            
            You have requested to reset your password. Please click the link below to reset your password:
            
            {reset_url}
            
            This link will expire in 24 hours.
            
            If you did not request this password reset, please ignore this email.
            
            Best regards,
            Finora Team
            '''
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            
            messages.success(request, 'Password reset link has been sent to your email.')
            
        except User.DoesNotExist:
            messages.error(request, 'No account found with this email address.')
        except Exception as e:
            messages.error(request, f'Error sending reset email: {str(e)}')
    
    return render(request, 'user_app/forgot_password.html')

def reset_password_view(request, token):
    try:
        reset_token = PasswordResetToken.objects.get(token=token, is_used=False)
        
        if reset_token.is_expired():
            messages.error(request, 'Password reset link has expired.')
            return redirect('user_app:forgot_password')
        
        if request.method == 'POST':
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            
            if password != confirm_password:
                messages.error(request, 'Passwords do not match.')
                return render(request, 'user_app/reset_password.html', {'token': token})
            
            # Update password
            user = reset_token.user
            user.set_password(password)
            user.save()
            
            # Mark token as used
            reset_token.is_used = True
            reset_token.save()
            
            messages.success(request, 'Password has been reset successfully. Please login.')
            return redirect('user_app:login')
        
        return render(request, 'user_app/reset_password.html', {'token': token})
        
    except PasswordResetToken.DoesNotExist:
        messages.error(request, 'Invalid or expired password reset link.')
        return redirect('user_app:forgot_password')
