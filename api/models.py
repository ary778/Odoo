# api/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class Company(models.Model):
    name = models.CharField(max_length=100)
    default_currency = models.CharField(max_length=3, default='USD')

    def __str__(self):
        return self.name

class User(AbstractUser):
    ROLE_CHOICES = (
        ('employee', 'Employee'),
        ('manager', 'Manager'),
        ('admin', 'Admin'),
    )
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='employee')
    manager = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'role__in': ['manager', 'admin']})

class ApprovalWorkflow(models.Model):
    name = models.CharField(max_length=100)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='workflows')

    def __str__(self):
        return self.name

class WorkflowStep(models.Model):
    workflow = models.ForeignKey(ApprovalWorkflow, on_delete=models.CASCADE, related_name='steps')
    approver = models.ForeignKey(User, on_delete=models.CASCADE)
    sequence = models.PositiveIntegerField()

    class Meta:
        ordering = ['sequence']

class ApprovalRule(models.Model):
    RULE_TYPE_CHOICES = (
        ('percentage', 'Percentage'),
        ('specific_approver', 'Specific Approver'),
    )
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='rules')
    rule_type = models.CharField(max_length=20, choices=RULE_TYPE_CHOICES)
    threshold_percentage = models.PositiveIntegerField(null=True, blank=True, help_text="e.g., 60 for 60%")
    specific_approver = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

class Expense(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('in_progress', 'In Progress'),
    )
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expenses')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='expenses')
    workflow = models.ForeignKey(ApprovalWorkflow, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    category = models.CharField(max_length=100)
    description = models.TextField()
    receipt = models.ImageField(upload_to='receipts/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.employee.username} - {self.amount} {self.currency}"

class Approval(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE, related_name='approvals')
    approver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='approvals_assigned')
    sequence = models.IntegerField(help_text="Approval order, e.g., 1 for Manager, 2 for Finance.")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    comment = models.TextField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['sequence']

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']