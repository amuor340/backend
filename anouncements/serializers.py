from rest_framework import serializers

from .models import Announcement


class AnnouncementSerializer(serializers.ModelSerializer):
    def validate_recipient(self, recipient):
        request = self.context.get("request")
        if request and request.user.is_authenticated and request.user.role != "SUPER_ADMIN":
            if not request.user.school_id or recipient.school_id != request.user.school_id:
                raise serializers.ValidationError("Recipients must belong to your school.")
        return recipient


    created_by_name = serializers.SerializerMethodField()
    recipient_name = serializers.SerializerMethodField()

    class Meta:
        model = Announcement
        fields = [
            "id",
            "title",
            "message",
            "priority",
            "target",
            "recipient",
            "recipient_name",
            "created_by",
            "created_by_name",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "created_by",
            "created_at",
            "updated_at",
        ]

    def get_recipient_name(self, obj):
        if obj.recipient:
            return (
                obj.recipient.get_full_name()
                or obj.recipient.username
            )
        return None

    def get_created_by_name(self, obj):
        if obj.created_by:
            return (
                obj.created_by.get_full_name()
                or obj.created_by.username
            )
        return None 