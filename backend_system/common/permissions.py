from rest_framework.permissions import IsAuthenticated


class IsAuthenticatedUser(IsAuthenticated):
    """
    Returns True if the request is from an authenticated full user otherwise False.
    """
    def has_permission(self, request, view):
        return super().has_permission(request, view)
