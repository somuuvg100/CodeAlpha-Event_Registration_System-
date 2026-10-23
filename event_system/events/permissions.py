from rest_framework import permissions


class IsEventCreatorOrStaff(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object or staff members to access it.
    """

    def has_object_permission(self, request, view, obj):
        # Staff members can do anything
        if request.user.is_staff:
            return True
        
        # Check if the user is the creator of the event
        return obj.created_by == request.user


class IsEventCreatorOrStaffOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow read access to all, but write access only to
    event creators or staff members.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the event creator or staff
        if request.user.is_staff:
            return True
        
        return obj.created_by == request.user
