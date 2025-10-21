from rest_framework.permissions import DjangoModelPermissions


class DjangoModelPermissionsOrAnonCreate(DjangoModelPermissions):
    """
    Permission class that allows anyone to create,
    but requires Django model permissions for other actions.
    """

    def has_permission(self, request, view):
        if view.action == "create":
            return True
        return super().has_permission(request, view)


class CreateOrListReadOnly(DjangoModelPermissions):
    """
    Permission class that allows anyone to create, list, and retrieve,
    but requires Django model permissions for other actions.
    """

    def has_permission(self, request, view):
        if view.action == "create" or view.action == "list":
            return True
        return super().has_permission(request, view)
