from rest_framework import serializers
from .models import HomeworkSubmission, ClassAssignment

class HomeworkSubmissionSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    assignment_title = serializers.CharField(source="assignment.title", read_only=True)
    class Meta:
        model = HomeworkSubmission
        fields = ["id", "assignment", "assignment_title", "student", "student_name", "text_response", "attachment", "status", "grade", "feedback", "submitted_at", "updated_at", "graded_by"]
        read_only_fields = ["id", "student", "status", "grade", "feedback", "submitted_at", "updated_at", "graded_by"]
    def get_fields(self):
        fields = super().get_fields()
        user = self.context.get("request").user if self.context.get("request") else None
        if user and getattr(user, "role", None) in {"TEACHER", "SCHOOL_ADMIN", "ACADEMIC_COORDINATOR"}:
            for name in ("status", "grade", "feedback", "graded_by"):
                fields[name].read_only = False
        return fields
    def get_student_name(self, obj):
        return f"{obj.student.first_name} {obj.student.last_name}".strip()
    def validate_assignment(self, assignment):
        user = self.context["request"].user
        if user.role != "SUPER_ADMIN" and assignment.school_id != user.school_id:
            raise serializers.ValidationError("Assignment must belong to your school.")
        return assignment
