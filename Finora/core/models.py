# Create your models here.
from django.db import models
from user_app.models import UserData, CompanyData


class Expense(models.Model):

    def update_status_from_approvals(self):
        approvals = self.approvals.all()
        if approvals.exists():
            if all(a.status == 'Approved' for a in approvals):
                self.status = 'Approved'
            elif any(a.status == 'Rejected' for a in approvals):
                self.status = 'Rejected'
            elif any(a.status == 'Pending' for a in approvals):
                self.status = 'Pending'
        else:
            self.status = 'Draft'
        self.save()

    def receipt_upload_path(instance, filename):
        return f"{instance.user.company.name}/receipts/user_{instance.user.id}/{filename}"

    # def validate_file_extension(value):
    #     import os
    #     ext = os.path.splitext(value.name)[1]
    #     valid_extensions = ['.pdf', '.jpg', '.jpeg', '.png']
    #     if not ext.lower() in valid_extensions:
    #         raise ValidationError('Unsupported file extension.')


    STATUS_CHOICES = [
        ('Draft', 'Draft'),
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    CATEGORY_CHOICES = [
        ('Travel', 'Travel'),
        ('Food', 'Food'),
        ('Office Supplies', 'Office Supplies'),
        ('Other', 'Other'),
    ]

    employee = models.ForeignKey(UserData, on_delete=models.CASCADE, related_name='expenses')
    description = models.TextField()
    date = models.DateField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Other')
    paid_by = models.ForeignKey(
        UserData,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='paid_expenses',
        help_text='The person responsible for paying this expense'
    )
    remarks = models.TextField(blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='INR')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Draft')
    receipt = models.FileField(upload_to=receipt_upload_path, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.user.name} - {self.category} - {self.amount} - {self.status}"


class ExpenseApproval(models.Model):
    STATUS_CHOICES = [
        ('Draft', 'Draft'),
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE, related_name='approvals')
    approver = models.ForeignKey(UserData, on_delete=models.CASCADE, related_name='approvals')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Expense: {self.expense.id} - Approver: {self.approver.email} - Status: {self.status}"


class ApprovalRules(models.Model):
    employee = models.ForeignKey(UserData, on_delete=models.CASCADE, related_name='employee_approval_rules')
    description = models.TextField()
    manager = models.ForeignKey(UserData, on_delete=models.CASCADE, related_name='manager_approval_rules')
    manager_approval = models.BooleanField(default=False)
    approvers = models.ManyToManyField(UserData, related_name='approver_approval_rules')
    approval_sequence = models.BooleanField(default=False)
    min_approval_percentage = models.IntegerField(default=51)
