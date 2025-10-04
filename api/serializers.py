# api/serializers.py
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import *
from .services import convert_currency

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['role'] = user.role
        return token

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'first_name', 'last_name', 'email', 'role']
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        # Manually set company from context provided by the view
        user.company = self.context['request'].user.company
        user.save()
        return user

class SignupSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(write_only=True, required=True)
    default_currency = serializers.CharField(write_only=True, required=True, max_length=3)
    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'first_name', 'last_name', 'company_name', 'default_currency')
        extra_kwargs = {'password': {'write_only': True}}
    def create(self, validated_data):
        company = Company.objects.create(name=validated_data['company_name'], default_currency=validated_data['default_currency'])
        user = User.objects.create_user(username=validated_data['username'], password=validated_data['password'], email=validated_data.get('email', ''), first_name=validated_data.get('first_name', ''), last_name=validated_data.get('last_name', ''), role='admin', company=company)
        return user

class WorkflowStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkflowStep
        fields = ['approver', 'sequence']

class ApprovalWorkflowSerializer(serializers.ModelSerializer):
    steps = WorkflowStepSerializer(many=True)
    class Meta:
        model = ApprovalWorkflow
        fields = ['id', 'name', 'company', 'steps']
        read_only_fields = ['company']
    def create(self, validated_data):
        steps_data = validated_data.pop('steps')
        workflow = ApprovalWorkflow.objects.create(**validated_data)
        for step_data in steps_data:
            WorkflowStep.objects.create(workflow=workflow, **step_data)
        return workflow

class ApprovalRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApprovalRule
        fields = '__all__'
        read_only_fields = ['company']

# ApprovalSerializer is forward-declared for ExpenseSerializer
class ApprovalSerializer(serializers.ModelSerializer):
    approver = UserSerializer(read_only=True)
    
    class Meta:
        model = Approval
        fields = ['id', 'approver', 'expense', 'sequence', 'status', 'comment', 'updated_at']

class ExpenseSerializer(serializers.ModelSerializer):
    employee = UserSerializer(read_only=True)
    # Use a string here to break the circular dependency
    approvals = ApprovalSerializer(many=True, read_only=True)
    converted_amount = serializers.SerializerMethodField()
    
    class Meta:
        model = Expense
        fields = ['id', 'employee', 'amount', 'currency', 'converted_amount', 'category', 'description', 'receipt', 'status', 'created_at', 'approvals', 'workflow']
        read_only_fields = ['employee', 'status', 'approvals', 'converted_amount']

    def get_converted_amount(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.company:
            return convert_currency(obj.amount, obj.currency, request.user.company.default_currency)
        return None

# Now define the ApprovalSerializer fully, including the nested ExpenseSerializer
class ApprovalSerializer(serializers.ModelSerializer):
    approver = UserSerializer(read_only=True)
    expense = ExpenseSerializer(read_only=True) 
    
    class Meta:
        model = Approval
        fields = ['id', 'approver', 'expense', 'sequence', 'status', 'comment', 'updated_at']

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'message', 'is_read', 'created_at']

class DashboardStatsSerializer(serializers.Serializer):
    pending_count = serializers.IntegerField()
    approved_count = serializers.IntegerField()
    total_approved_amount = serializers.DecimalField(max_digits=12, decimal_places=2)