# api/services.py
from .models import Approval, Notification, Expense, ApprovalRule, User
import requests

def create_approval_workflow(expense: Expense):
    if expense.workflow:
        for step in expense.workflow.steps.all():
            Approval.objects.create(expense=expense, approver=step.approver, sequence=step.sequence)
            if step.sequence == 1:
                create_notification(user=step.approver, message=f"New expense from {expense.employee.username} needs your approval.")
    elif expense.employee.manager:
        Approval.objects.create(expense=expense, approver=expense.employee.manager, sequence=1)
        create_notification(user=expense.employee.manager, message=f"New expense from {expense.employee.username} needs your approval.")

def evaluate_conditional_rules(expense: Expense, current_approver: User):
    rules = ApprovalRule.objects.filter(company=expense.company)
    approvals = expense.approvals.all()
    for rule in rules:
        if rule.rule_type == 'specific_approver' and rule.specific_approver == current_approver:
            return 'approved'
        if rule.rule_type == 'percentage':
            approved_count = approvals.filter(status='approved').count()
            total_approvers = approvals.count()
            if total_approvers > 0:
                approval_percentage = (approved_count / total_approvers) * 100
                if approval_percentage >= rule.threshold_percentage:
                    return 'approved'
    return None

def process_approval_action(approval: Approval, decision: str, comment: str):
    approval.status = decision
    approval.comment = comment
    approval.save()
    expense = approval.expense
    create_notification(user=expense.employee, message=f"Your expense '{expense.description}' was {decision} by {approval.approver.username}.")
    if decision == 'rejected':
        expense.status = 'rejected'
        expense.save()
        return
    rule_decision = evaluate_conditional_rules(expense, approval.approver)
    if rule_decision == 'approved':
        expense.status = 'approved'
        expense.save()
        create_notification(user=expense.employee, message=f"Expense auto-approved by conditional rule.")
        return
    next_approval = expense.approvals.filter(sequence=approval.sequence + 1).first()
    if next_approval:
        expense.status = 'in_progress'
        expense.save()
        create_notification(user=next_approval.approver, message=f"Expense from {expense.employee.username} is ready for your approval.")
    else:
        expense.status = 'approved'
        expense.save()

def create_notification(user, message):
    Notification.objects.create(user=user, message=message)

def perform_ocr_on_receipt(image_file):
    return {'amount': 125.50, 'description': 'Mocked from receipt', 'category': 'Meals'}

def convert_currency(amount, from_currency, to_currency):
    if from_currency == to_currency: return amount
    try:
        response = requests.get(f"https://api.exchangerate-api.com/v4/latest/{from_currency}")
        response.raise_for_status()
        rate = response.json()['rates'].get(to_currency)
        return round(float(amount) * rate, 2) if rate else None
    except requests.RequestException:
        return None