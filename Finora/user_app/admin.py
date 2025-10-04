from django.contrib import admin
from .models import CompanyData, UserData, PasswordResetToken

# Register your models here.

@admin.register(CompanyData)
class CompanyDataAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'currency', 'created_at')
    list_filter = ('country', 'currency', 'created_at')
    search_fields = ('name', 'country')

@admin.register(UserData)
class UserDataAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'role', 'company', 'manager', 'created_at')
    list_filter = ('role', 'company', 'created_at')
    search_fields = ('name', 'email', 'user__username')
    list_select_related = ('company', 'manager', 'user')

@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'created_at', 'expires_at', 'is_used')
    list_filter = ('is_used', 'created_at', 'expires_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('token', 'created_at')
