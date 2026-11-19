from django.db.models import Q
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from accounts.models import CustomUser
from .models import InternalMessage, Notification
from .message_serializers import InternalMessageSerializer


class InternalMessageViewSet(viewsets.ModelViewSet):
    serializer_class = InternalMessageSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_queryset(self):
        user = self.request.user
        qs = InternalMessage.objects.select_related("school", "sender", "recipient")
        if user.role == CustomUser.Role.SUPER_ADMIN:
            return qs.filter(Q(sender=user) | Q(recipient=user))
        if not user.school_id:
            return qs.none()
        return qs.filter(school_id=user.school_id).filter(Q(sender=user) | Q(recipient=user))

    def perform_create(self, serializer):
        sender = self.request.user
        recipient = serializer.validated_data["recipient"]
        if sender.role == CustomUser.Role.SUPER_ADMIN:
            if recipient.role != CustomUser.Role.SCHOOL_ADMIN:
                raise PermissionDenied("The Pseudosphere System Admin can message school administrators only.")
            school = recipient.school
            if school is None:
                raise PermissionDenied("Platform messages must target a user assigned to a school.")
        else:
            school = sender.school
            if school is None or recipient.school_id != school.id:
                raise PermissionDenied("You can only message users in your own school.")
        message = serializer.save(sender=sender, school=school)
        Notification.objects.create(
            recipient=recipient,
            triggered_by=sender,
            notification_type=Notification.NotificationType.GENERAL,
            title=f"New message: {message.subject}",
            message=f"You received a message from {sender.get_full_name() or sender.username}.",
        )

    @action(detail=True, methods=["post"])
    def mark_read(self, request, pk=None):
        message = self.get_object()
        if message.recipient_id != request.user.id:
            raise PermissionDenied("Only the recipient can mark this message as read.")
        message.is_read = True
        message.read_at = timezone.now()
        message.save(update_fields=["is_read", "read_at"])
        return Response(self.get_serializer(message).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"])
    def inbox(self, request):
        qs = self.get_queryset().filter(recipient=request.user)
        return Response(self.get_serializer(qs, many=True).data)

    @action(detail=False, methods=["get"])
    def sent(self, request):
        qs = self.get_queryset().filter(sender=request.user)
        return Response(self.get_serializer(qs, many=True).data)
