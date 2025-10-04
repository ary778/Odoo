# api/urls.py (updated)
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    SignupView, UserViewSet, ExpenseViewSet, ApprovalViewSet,
    NotificationViewSet, DashboardStatsView
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'expenses', ExpenseViewSet, basename='expense')
router.register(r'approvals', ApprovalViewSet, basename='approval')
router.register(r'notifications', NotificationViewSet, basename='notification')

urlpatterns = [
    path('', include(router.urls)),
    path('signup/', SignupView.as_view(), name='signup'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('dashboard-stats/', DashboardStatsView.as_view(), name='dashboard_stats'),
]