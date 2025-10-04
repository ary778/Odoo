# api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import MyTokenObtainPairView, SignupView, UserViewSet, ExpenseViewSet, ApprovalViewSet, NotificationViewSet, DashboardStatsView, ApprovalWorkflowViewSet, ApprovalRuleViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'expenses', ExpenseViewSet, basename='expense')
router.register(r'approvals', ApprovalViewSet, basename='approval')
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'workflows', ApprovalWorkflowViewSet, basename='workflow')
router.register(r'rules', ApprovalRuleViewSet, basename='rule')

urlpatterns = [
    path('', include(router.urls)),
    path('signup/', SignupView.as_view(), name='signup'),
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('dashboard-stats/', DashboardStatsView.as_view(), name='dashboard_stats'),
]