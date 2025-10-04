from django.shortcuts import render
from django.core.mail import send_mail
from django.http import HttpResponse

def send_test_email(request):
    send_mail(
        subject="Test Email from Django",
        message="Hello! This is a test email sent via Gmail SMTP.",
        from_email=None,  # will use DEFAULT_FROM_EMAIL
        recipient_list=["vivek16903@gmail.com"],
        fail_silently=False,
    )

def index(request):
    print("Sending test email")
    # send_test_email(request)
    print("Test email sent successfully")
    return render(request, 'index.html')


