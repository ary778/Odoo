# api/permissions.py (New File)
from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdminOrReadOnly(BasePermission):
    """
    Custom permission to only allow admins to edit or create objects.
    Other authenticated users have read-only access.
    """
    def has_permission(self, request, view):
        # Allow all authenticated users to list or view (GET, HEAD, OPTIONS)
        if request.method in SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the admin users.
        return request.user and request.user.role == 'admin'

class IsOwnerOrManager(BasePermission):
    """
    Custom permission for expenses. Allows an employee to view their own,
    and a manager/admin to view/edit.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner's manager or an admin.
        return obj.employee.manager == request.user or request.user.role == 'admin'