from rest_framework.permissions import BasePermission, SAFE_METHODS
import logging
logger = logging.getLogger(__name__)

class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        logger.error(f"User: {request.user}")  # This will be more visible in logs
        logger.error(f"Is staff: {request.user.is_staff}")
        logger.error(f"Is authenticated: {request.user.is_authenticated}")
        if request.method in SAFE_METHODS:
            return True
            
        # Write permissions are only allowed to admin users
        return request.user and request.user.is_staff