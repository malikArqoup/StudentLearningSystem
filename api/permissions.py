from rest_framework.permissions import BasePermission


# Central place for permission decisions. Views should reference permission
# classes defined here instead of checking request.user.role (or similar)
# directly, and instead of importing DRF's built-in permission classes.


class IsAuthenticatedUser(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)


class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == "admin"
        )