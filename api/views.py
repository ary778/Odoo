# api/views.py
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import viewsets, generics, permissions, status, views
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import *
from .serializers import *
from .services import *
from .permissions import IsAdminOrReadOnly

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class SignupView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = SignupSerializer

class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    serializer_class = UserSerializer
    
    def get_queryset(self):
        return User.objects.filter(company=self.request.user.company)
    
    def get_serializer_context(self):
        return {'request': self.request}
    
    def perform_create(self, serializer):
        # When an admin creates a user, automatically assign them to the admin's company.
        user = serializer.save(company=self.request.user.company)
        # NEW: Send email notification
        subject = 'Your New Account has been Created'
        message = f'Hello {user.username},\n\nAn account has been created for you in the Expensify portal. You can now log in with the password provided.'
        from_email = 'admin@expensify.com'
        recipient_list = [user.email]
        send_mail(subject, message, from_email, recipient_list)

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
        # Correctly save the expense first
        expense = serializer.save(employee=self.request.user, company=self.request.user.company)
        # Then, create the approval workflow for that expense
        create_approval_workflow(expense)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def override(self, request, pk=None):
        expense = self.get_object()
        decision = request.data.get('decision')
        if decision not in ['approved', 'rejected']:
            return Response({'error': 'Decision must be approved or rejected.'}, status=status.HTTP_400_BAD_REQUEST)
        
        expense.status = decision
        expense.save()
        create_notification(
            user=expense.employee,
            message=f"Your expense '{expense.description}' was overridden to '{decision}' by an administrator."
        )
        return Response(ExpenseSerializer(expense, context={'request': request}).data)
    
    @action(detail=True, methods=['post'], url_path='upload-receipt')
    def upload_receipt(self, request, pk=None):
        expense = self.get_object()
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

class ApprovalViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ApprovalSerializer

    def get_queryset(self):
        return Approval.objects.filter(approver=self.request.user)

    @action(detail=True, methods=['post'])
    def act(self, request, pk=None):
        approval = self.get_object()
        decision, comment = request.data.get('decision'), request.data.get('comment', '')
        if approval.approver != request.user:
            return Response({'error': 'Not authorized.'}, status=status.HTTP_403_FORBIDDEN)
        if approval.status != 'pending':
            return Response({'error': 'This approval has already been processed.'}, status=status.HTTP_400_BAD_REQUEST)
        if decision not in ['approved', 'rejected']:
            return Response({'error': "Decision must be 'approved' or 'rejected'."}, status=status.HTTP_400_BAD_REQUEST)
        process_approval_action(approval, decision, comment)
        return Response(ExpenseSerializer(approval.expense, context={'request': request}).data)

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
        user, queryset = request.user, Expense.objects.filter(company=request.user.company)
        if user.role == 'manager':
            queryset = queryset.filter(employee__manager=user)
        elif user.role == 'employee':
            queryset = queryset.filter(employee=user)
        stats = {
            'pending_count': queryset.filter(status__in=['pending', 'in_progress']).count(),
            'approved_count': queryset.filter(status='approved').count(),
            'total_approved_amount': queryset.filter(status='approved').aggregate(total=Sum('amount'))['total'] or 0
        }
        return Response(DashboardStatsSerializer(stats).data)

class ApprovalWorkflowViewSet(viewsets.ModelViewSet):
    serializer_class = ApprovalWorkflowSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]

    def get_queryset(self):
        return ApprovalWorkflow.objects.filter(company=self.request.user.company)
    
    def perform_create(self, serializer):
        serializer.save(company=self.request.user.company)

class ApprovalRuleViewSet(viewsets.ModelViewSet):
    serializer_class = ApprovalRuleSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    
    def get_queryset(self):
        return ApprovalRule.objects.filter(company=self.request.user.company)
    
    def perform_create(self, serializer):
        serializer.save(company=self.request.user.company)