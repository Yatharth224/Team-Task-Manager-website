from rest_framework.permissions import BasePermission
from .models import ProjectMember


def get_membership(project, user):
    try:
        return ProjectMember.objects.get(project=project, user=user)
    except ProjectMember.DoesNotExist:
        return None


class IsProjectMember(BasePermission):
    """Allow access only to members of the project."""

    def has_object_permission(self, request, view, obj):
        return get_membership(obj, request.user) is not None


class IsProjectAdmin(BasePermission):
    """Allow write access only to project admins."""

    def has_object_permission(self, request, view, obj):
        seat = get_membership(obj, request.user)
        return seat is not None and seat.role == ProjectMember.ADMIN