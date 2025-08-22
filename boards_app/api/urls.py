from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BoardViewSet, BoardActiveListView, BoardDeactivateView

router = DefaultRouter()
router.register(r'boards', BoardViewSet, basename='board')

urlpatterns = [
    path('boards/active/', BoardActiveListView.as_view(), name='board-active'),
    path('boards/<int:pk>/deactivate/', BoardDeactivateView.as_view(), name='board-deactivate'),
    path('', include(router.urls)),
]
