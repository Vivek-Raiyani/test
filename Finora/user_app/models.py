from django.db import models
from django.contrib.auth.models import User


class ComapanyData(models.Model):
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    currency = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return F"Company: {self.name} - Country: {self.country} - Currency: {self.currency}"
    


# Create your models here.
class UserData(models.Model):
    ROLE_CHOICES = [
        ('Admin', 'Admin'),
        ('Manager', 'Manager'),
        ('Employee', 'Employee'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='Employee')
    company = models.ForeignKey(ComapanyData, on_delete=models.CASCADE)
    manager = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True, related_name="team")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

