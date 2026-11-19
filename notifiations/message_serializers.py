from rest_framework import serializers
from accounts.models import CustomUser
from .models import InternalMessage


class InternalMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()
    recipient_name = serializers.SerializerMethodField()

    class Meta:
        model = InternalMessage
        fields = ["id", "school", "sender", "sender_name", "recipient", "recipient_name", "subject", "body", "is_read", "read_at", "created_at"]
        read_only_fields = ["id", "school", "sender", "sender_name", "recipient_name", "is_read", "read_at", "created_at"]

    def get_sender_name(self, obj):
        return obj.sender.get_full_name() or obj.sender.username

    def get_recipient_name(self, obj):
        return obj.recipient.get_full_name() or obj.recipient.username

    def validate_recipient(self, recipient):
        request = self.context.get("request")
        if not request:
            return recipient
        sender = request.user
        if recipient.id == sender.id:
            raise serializers.ValidationError("Choose another user as the recipient.")
        if sender.role in [CustomUser.Role.PARENT, CustomUser.Role.STUDENT] and recipient.role not in [CustomUser.Role.SCHOOL_ADMIN, CustomUser.Role.ACADEMIC_COORDINATOR, CustomUser.Role.TEACHER, CustomUser.Role.ACCOUNTANT]:
            raise serializers.ValidationError("Parents and students can message school staff, teachers, or the accountant.")
        if sender.role == CustomUser.Role.SUPER_ADMIN and recipient.role != CustomUser.Role.SCHOOL_ADMIN:
            raise serializers.ValidationError("The Pseudosphere System Admin can message school administrators only.")
        if sender.role != CustomUser.Role.SUPER_ADMIN and (not sender.school_id or recipient.school_id != sender.school_id):
            raise serializers.ValidationError("You can only message users in your own school.")
        if not recipient.is_active:
            raise serializers.ValidationError("This recipient account is inactive.")
        return recipient

    def validate(self, attrs):
        if len(attrs.get("body", "").strip()) < 1:
            raise serializers.ValidationError({"body": "Message body cannot be empty."})
        return attrs
