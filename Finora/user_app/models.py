from django.db import models
from django.contrib.auth.models import User


class CompanyData(models.Model):
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    currency = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Company: {self.name} - Country: {self.country} - Currency: {self.currency}"
    


# Create your models here.
class UserData(models.Model):
    ROLE_CHOICES = [
        ('Admin', 'Admin'),
        ('Manager', 'Manager'),
        ('Employee', 'Employee'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='Employee')
    company = models.ForeignKey(CompanyData, on_delete=models.CASCADE, related_name="employees")
    manager = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True, related_name="team")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.email = self.user.email
        self.name = self.user.username
        self.user.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Email: {self.email} - Role: {self.role} - Company: {self.company.name}"

