from common.permissions import IsAuthenticatedUser


class FlightsPermissions(IsAuthenticatedUser):
    action_perm_map = {
        'list': 'view',
        'retrieve': 'view',
        'create': 'create',
        'update': 'update',
        'destroy': 'delete',
    }

    def has_permission(self, request, view):
        if super().has_permission(request, view):
            if view.action in ['create', 'update']:
                return request.user.is_staff

            if view.action == 'destroy':
                return (request.user.is_staff and request.user.is_superuser)
            return True
        return False
