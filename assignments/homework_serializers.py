from rest_framework import serializers
from .models import ClassAssignment


class ClassAssignmentSerializer(serializers.ModelSerializer):
    classroom_name = serializers.SerializerMethodField()
    subject_name = serializers.CharField(source="subject.name", read_only=True)
    teacher_name = serializers.SerializerMethodField()
    attachment_url = serializers.SerializerMethodField()

    class Meta:
        model = ClassAssignment
        fields = ["id", "school", "classroom", "classroom_name", "subject", "subject_name", "created_by", "teacher_name", "title", "instructions", "attachment", "attachment_url", "due_date", "created_at", "updated_at"]
        read_only_fields = ["id", "school", "created_by", "created_at", "updated_at", "teacher_name"]

    def get_classroom_name(self, obj):
        return str(obj.classroom)

    def get_teacher_name(self, obj):
        return obj.created_by.get_full_name() or obj.created_by.username

    def get_attachment_url(self, obj):
        request = self.context.get("request")
        if not obj.attachment:
            return None
        url = obj.attachment.url
        return request.build_absolute_uri(url) if request else url

    def validate_attachment(self, value):
        if value:
            if value.size > 10 * 1024 * 1024:
                raise serializers.ValidationError("Attachments must be 10 MB or smaller.")
            allowed = {".pdf", ".doc", ".docx", ".ppt", ".pptx", ".png", ".jpg", ".jpeg"}
            from pathlib import Path
            if Path(value.name).suffix.lower() not in allowed:
                raise serializers.ValidationError("Allowed attachments: PDF, Word, PowerPoint, PNG, or JPEG files.")
        return value

    def validate(self, attrs):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            user = request.user
            classroom = attrs.get("classroom", getattr(self.instance, "classroom", None))
            subject = attrs.get("subject", getattr(self.instance, "subject", None))
            if user.role != "SUPER_ADMIN":
                if not user.school_id or not classroom or classroom.school_id != user.school_id:
                    raise serializers.ValidationError({"classroom": "Choose a classroom from your school."})
                if subject and subject.school_id != user.school_id:
                    raise serializers.ValidationError({"subject": "Choose a subject from your school."})
        return attrs
