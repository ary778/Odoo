# api/admin.py (updated)
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    Company, User, Expense, Approval, Notification,
    ApprovalWorkflow, WorkflowStep, ApprovalRule
)

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('username', 'email', 'role', 'company', 'manager')
    fieldsets = UserAdmin.fieldsets + ((None, {'fields': ('company', 'role', 'manager')}),)
    add_fieldsets = UserAdmin.add_fieldsets + ((None, {'fields': ('company', 'role', 'manager')}),)

admin.site.register(Company)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Expense)
admin.site.register(Approval)
admin.site.register(Notification)
admin.site.register(ApprovalWorkflow)
admin.site.register(WorkflowStep)
admin.site.register(ApprovalRule)