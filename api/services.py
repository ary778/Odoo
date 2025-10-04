# api/services.py (new file)
from .models import Approval, Notification, Expense

def create_approval_workflow(expense: Expense):
    """
    Creates the necessary Approval objects for an expense based on a defined workflow.
    For this example, it's a simple Employee -> Manager workflow.
    This can be expanded to read from a rules engine.
    """
    employee = expense.employee
    if employee.manager:
        # Step 1: Manager Approval
        Approval.objects.create(
            expense=expense,
            approver=employee.manager,
            sequence=1
        )
        # Notify the manager
        create_notification(
            user=employee.manager,
            message=f"New expense report from {employee.username} for {expense.amount} {expense.currency} needs your approval."
        )

def process_approval_action(approval: Approval, decision: str, comment: str):
    """
    Processes an approval or rejection, updates statuses, and notifies users.
    Returns True if the workflow is complete, False otherwise.
    """
    approval.status = decision
    approval.comment = comment
    approval.save()
    
    expense = approval.expense
    
    # Notify employee of the action
    create_notification(
        user=expense.employee,
        message=f"Your expense '{expense.description}' was {decision} by {approval.approver.username}."
    )
    
    if decision == 'rejected':
        expense.status = 'rejected'
        expense.save()
        return True # Workflow ends on rejection

    # Check for next approver
    next_approval = expense.approvals.filter(sequence=approval.sequence + 1).first()
    
    if next_approval:
        expense.status = 'in_progress'
        expense.save()
        # Notify next approver
        create_notification(
            user=next_approval.approver,
            message=f"Expense from {expense.employee.username} is ready for your approval."
        )
        return False # Workflow continues
    else:
        # This was the final approval
        expense.status = 'approved'
        expense.save()
        return True # Workflow is complete

def create_notification(user, message):
    Notification.objects.create(user=user, message=message)

def perform_ocr_on_receipt(image_file):
    """
    Placeholder for OCR logic. In a real app, this would integrate with a
    service like Google Cloud Vision or a library like Tesseract.
    """
    #
    # Example: from google.cloud import vision
    # client = vision.ImageAnnotatorClient()
    # content = image_file.read()
    # image = vision.Image(content=content)
    # response = client.text_detection(image=image)
    # texts = response.text_annotations
    # extracted_text = texts[0].description if texts else ""
    #
    # Here, we'll just return mock data.
    return {
        'amount': 125.50,
        'description': 'Mocked from receipt: Lunch at The Grand Hotel',
        'category': 'Meals'
    }