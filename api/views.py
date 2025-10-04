# api/views.py (Updated)
from rest_framework import viewsets, generics, permissions, status, views
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Q
from .models import User, Expense, Approval, Notification
from .serializers import (
    UserSerializer, SignupSerializer, ExpenseSerializer, 
    ApprovalSerializer, NotificationSerializer, DashboardStatsSerializer
)
from .services import create_approval_workflow, process_approval_action, perform_ocr_on_receipt
from .permissions import IsAdminOrReadOnly # Import the new permission

# --- SignupView remains the same ---
class SignupView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = SignupSerializer

# --- UserViewSet is now more secure ---
class UserViewSet(viewsets.ModelViewSet):
    # Use our custom permission class
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    serializer_class = UserSerializer

    def get_queryset(self):
        # Users should only see other users in their own company
        return User.objects.filter(company=self.request.user.company)

# --- ExpenseViewSet uses IsAuthenticated, as its logic is handled by get_queryset ---
class ExpenseViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ExpenseSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Expense.objects.filter(company=user.company)
        elif user.role == 'manager':
            return Expense.objects.filter(employee__manager=user, company=user.company)
        else:
            return Expense.objects.filter(employee=user)

    def perform_create(self, serializer):
        expense = serializer.save(employee=self.request.user, company=self.request.user.company)
        create_approval_workflow(expense)

    @action(detail=True, methods=['post'], url_path='upload-receipt')
    def upload_receipt(self, request, pk=None):
        expense = self.get_object()
        # Add a check to ensure only the owner can upload a receipt
        if expense.employee != request.user:
            return Response({'error': 'You can only upload receipts for your own expenses.'}, status=status.HTTP_403_FORBIDDEN)
            
        receipt_file = request.FILES.get('receipt')
        if not receipt_file:
            return Response({'error': 'No receipt file provided.'}, status=status.HTTP_400_BAD_REQUEST)
        
        expense.receipt = receipt_file
        expense.save()
        
        ocr_data = perform_ocr_on_receipt(receipt_file)
        
        expense.amount = ocr_data.get('amount', expense.amount)
        expense.description = ocr_data.get('description', expense.description)
        expense.save()
        
        return Response({
            'message': 'Receipt uploaded and processed.',
            'ocr_data': ocr_data,
            'expense': ExpenseSerializer(expense).data
        })

# --- The rest of the views (ApprovalViewSet, NotificationViewSet, DashboardStatsView) remain the same ---
class ApprovalViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ApprovalSerializer

    def get_queryset(self):
        return Approval.objects.filter(approver=self.request.user)

    @action(detail=True, methods=['post'])
    def act(self, request, pk=None):
        approval = self.get_object()
        decision = request.data.get('decision')
        comment = request.data.get('comment', '')

        if approval.approver != request.user:
            return Response({'error': 'Not authorized.'}, status=status.HTTP_403_FORBIDDEN)
        if approval.status != 'pending':
            return Response({'error': 'This approval has already been processed.'}, status=status.HTTP_400_BAD_REQUEST)
        if decision not in ['approved', 'rejected']:
            return Response({'error': "Decision must be 'approved' or 'rejected'."}, status=status.HTTP_400_BAD_REQUEST)

        process_approval_action(approval, decision, comment)
        return Response(ExpenseSerializer(approval.expense).data)

class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        self.get_queryset().update(is_read=True)
        return Response(status=status.HTTP_204_NO_CONTENT)

class DashboardStatsView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        queryset = Expense.objects.filter(company=user.company)

        if user.role == 'manager':
            queryset = queryset.filter(employee__manager=user)
        elif user.role == 'employee':
            queryset = queryset.filter(employee=user)

        stats = {
            'pending_count': queryset.filter(status__in=['pending', 'in_progress']).count(),
            'approved_count': queryset.filter(status='approved').count(),
            'total_approved_amount': queryset.filter(status='approved').aggregate(total=Sum('amount'))['total'] or 0
        }
        serializer = DashboardStatsSerializer(stats)
        return Response(serializer.data)