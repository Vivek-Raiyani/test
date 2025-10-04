from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.http import HttpResponse
# from django.contrib.auth.decorators import login_required
from user_app.models import UserData

def send_test_email(request):
    send_mail(
        subject="Test Email from Django",
        message="Hello! This is a test email sent via Gmail SMTP.",
        from_email=None,  # will use DEFAULT_FROM_EMAIL
        recipient_list=["vivek16903@gmail.com"],
        fail_silently=False,
    )

def index(request):
    if request.user.is_authenticated:
        try:
            user_data = UserData.objects.get(user=request.user)
            if user_data.role == 'Admin':
                return redirect('admin_dashboard')
        except UserData.DoesNotExist:
            pass
    
    print("Sending test email")
    # send_test_email(request)
    print("Test email sent successfully")
    return render(request, 'index.html')


