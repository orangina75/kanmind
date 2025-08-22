from rest_framework import viewsets, status, generics, mixins
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, PermissionDenied
from django.contrib.auth import get_user_model

from boards_app.models import Board
from .serializers import (
    BoardListSerializer,
    BoardCreateSerializer,
    BoardDetailSerializer,
    BoardUpdateSerializer,
    BoardUpdateResponseSerializer,  
)
from .permissions import IsBoardMemberOrOwner, IsBoardOwner

User = get_user_model()


class BoardViewSet(viewsets.ModelViewSet):
    queryset = Board.objects.all()
    permission_classes = [IsAuthenticated, IsBoardMemberOrOwner]
    lookup_field = "pk"

    def get_serializer_class(self):
        if self.action == "list":
            return BoardListSerializer
        elif self.action == "create":
            return BoardCreateSerializer
        elif self.action in ["retrieve", "update", "partial_update"]:
            return BoardUpdateSerializer
        return BoardDetailSerializer

    def get_queryset(self):
        user = self.request.user
        return (Board.objects.filter(owner=user) | Board.objects.filter(members=user)).distinct()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        board = serializer.save() 
        return Response(BoardListSerializer(board).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.get("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial, context={"request": request})
        serializer.is_valid(raise_exception=True)
        board = serializer.save()
        return Response(BoardUpdateResponseSerializer(board).data, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        board = self.get_object()
        if board.owner != request.user:
            return Response(
                {"detail": "Nur der Eigentümer darf dieses Board löschen."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        tasks = board.tasks.all()
        for task in tasks:
            task.comments.all().delete()
            task.delete()

        board.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class BoardActiveListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        boards = Board.objects.filter(owner=request.user) | Board.objects.filter(members=request.user)
        serializer = BoardListSerializer(boards.distinct(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class BoardDeactivateView(generics.GenericAPIView, mixins.UpdateModelMixin):
    permission_classes = [IsAuthenticated, IsBoardOwner]
    queryset = Board.objects.all()
    serializer_class = BoardDetailSerializer

    def post(self, request, pk):
        board = self.get_object()
        board.is_active = False
        board.save()
        serializer = self.get_serializer(board)
        return Response(serializer.data, status=status.HTTP_200_OK)
