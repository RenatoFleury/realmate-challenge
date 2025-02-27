from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    webhook_view,
    ConversationViewSet,
    ConversationView,
    MessageViewSet,
)

router = DefaultRouter()
router.register(r'conversations', ConversationViewSet)
router.register(r'messages', MessageViewSet)

urlpatterns = [
    path("webhook/", webhook_view, name="webhook"),
    path('conversations/<str:pk>/', ConversationView.as_view({'get': 'retrieve'}), name='conversations'),
    path('api-auth/', include(router.urls)),
]