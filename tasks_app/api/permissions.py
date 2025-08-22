from rest_framework.permissions import BasePermission


class IsTaskAssigneeOrBoardMember(BasePermission):

    def has_object_permission(self, request, view, obj):
        return (
            request.user == obj.assignee
            or request.user == obj.created_by
            or request.user == obj.board.owner
            or request.user in obj.board.members.all()
        )

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
