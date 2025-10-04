# api/serializers.py
from rest_framework import serializers
from .models import Company, User, Expense, Approval, Notification

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'name', 'default_currency']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'role']

class SignupSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(write_only=True, required=True)
    default_currency = serializers.CharField(write_only=True, required=True, max_length=3)
    
    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'first_name', 'last_name', 'company_name', 'default_currency')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # Create the company first
        company = Company.objects.create(
            name=validated_data['company_name'],
            default_currency=validated_data['default_currency']
        )
        # Then create the user, assigning them as an admin to the new company
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data.get('email', ''),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            role='admin',
            company=company
        )
        return user

class ApprovalSerializer(serializers.ModelSerializer):
    approver = UserSerializer(read_only=True)
    class Meta:
        model = Approval
        fields = ['id', 'approver', 'sequence', 'status', 'comment', 'updated_at']

class ExpenseSerializer(serializers.ModelSerializer):
    employee = UserSerializer(read_only=True)
    approvals = ApprovalSerializer(many=True, read_only=True)

    class Meta:
        model = Expense
        fields = ['id', 'employee', 'amount', 'currency', 'category', 'description', 'receipt', 'status', 'created_at', 'approvals']
        read_only_fields = ['employee', 'status', 'approvals']

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'message', 'is_read', 'created_at']

class DashboardStatsSerializer(serializers.Serializer):
    pending_count = serializers.IntegerField()
    approved_count = serializers.IntegerField()
    total_approved_amount = serializers.DecimalField(max_digits=12, decimal_places=2)