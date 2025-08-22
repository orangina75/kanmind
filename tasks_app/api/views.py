from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from tasks_app.models import Task, Comment
from .serializers import (
    TaskCreateSerializer,
    TaskResponseSerializer,
    CommentSerializer,
)
from .permissions import IsTaskAssigneeOrBoardMember


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    permission_classes = [IsAuthenticated, IsTaskAssigneeOrBoardMember]

    def get_queryset(self):
        user = self.request.user
        return (
            Task.objects.filter(board__owner=user)
            | Task.objects.filter(board__members=user)
            | Task.objects.filter(assignee=user)
            | Task.objects.filter(created_by=user)
        ).distinct()

    def get_serializer_class(self):
        if self.action in ["list", "assigned_to_me", "reviewing"]:
            return TaskResponseSerializer
        elif self.action == "create":
            return TaskCreateSerializer
        return TaskResponseSerializer

    def perform_create(self, serializer):
        task = serializer.save(created_by=self.request.user)
        response_serializer = TaskResponseSerializer(task)
        self.response_data = response_serializer.data

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(self.response_data, status=status.HTTP_201_CREATED, headers=headers)

    def destroy(self, request, *args, **kwargs):
        task = self.get_object()
        if task.board.owner != request.user and task.assignee != request.user:
            raise PermissionDenied("Nur Owner oder Assignee dürfen löschen.")
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["get", "post"], url_path="comments")
    def comments(self, request, pk=None):
        task = self.get_object()
        if request.method == "GET":
            serializer = CommentSerializer(task.comments.all(), many=True)
            return Response(serializer.data)
        elif request.method == "POST":
            serializer = CommentSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(task=task, author=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["delete"], url_path=r"comments/(?P<comment_id>\d+)")
    def delete_comment(self, request, pk=None, comment_id=None):
        task = self.get_object()
        try:
            comment = task.comments.get(pk=comment_id)
        except Comment.DoesNotExist:
            return Response({"detail": "Comment not found."}, status=status.HTTP_404_NOT_FOUND)

        if comment.author != request.user:
            return Response({"detail": "Not allowed."}, status=status.HTTP_403_FORBIDDEN)

        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["get"], url_path="assigned-to-me")
    def assigned_to_me(self, request):
        tasks = Task.objects.filter(assignee=request.user)
        serializer = TaskResponseSerializer(tasks, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=["get"], url_path="reviewing")
    def reviewing(self, request):
        tasks = Task.objects.filter(reviewer=request.user)
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)
