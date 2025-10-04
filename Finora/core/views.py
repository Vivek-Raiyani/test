from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from user_app.models import UserData

# Create your views here.

@login_required
def dashboard(request):
    """Main dashboard that redirects users based on their role"""
    try:
        user_data = UserData.objects.get(user=request.user)
        
        # Redirect employees to their specific dashboard
        if user_data.role == 'Employee':
            return redirect('core:employee_dashboard')
        # For now, show the general dashboard for other roles
        # Later we can add manager and admin dashboards
        else:
            return render(request, 'core/dashboard.html')
            
    except UserData.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('user_app:login')
