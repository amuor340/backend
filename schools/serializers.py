from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from . import education
from .models import School

User = get_user_model()


def validate_education_systems(value):
    """A school must teach at least one known curriculum."""
    if not isinstance(value, (list, tuple)) or not value:
        raise serializers.ValidationError("Choose at least one education system.")
    cleaned = []
    for item in value:
        if not education.is_valid_system(item):
            raise serializers.ValidationError(f"Unknown education system: {item}.")
        if item not in cleaned:
            cleaned.append(item)
    return cleaned


class SchoolRegistrationSerializer(serializers.Serializer):
    school_name = serializers.CharField(max_length=180)
    registration_number = serializers.CharField(max_length=100, required=False, allow_blank=True)
    school_email = serializers.EmailField()
    school_phone = serializers.CharField(max_length=40, required=False, allow_blank=True)
    address = serializers.CharField(required=False, allow_blank=True)
    admin_first_name = serializers.CharField(max_length=150)
    admin_last_name = serializers.CharField(max_length=150)
    admin_email = serializers.EmailField()
    admin_username = serializers.RegexField(r"^[\w.@+-]+$", max_length=150)
    admin_password = serializers.CharField(write_only=True, min_length=8, trim_whitespace=False)
    education_systems = serializers.ListField(
        child=serializers.CharField(), required=False, default=lambda: [education.DEFAULT_SYSTEM]
    )

    def validate_education_systems(self, value):
        return validate_education_systems(value)

    def validate_admin_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return value

    def validate_admin_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value

    def validate_admin_password(self, value):
        try:
            validate_password(value)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(list(exc.messages))
        return value


class SchoolSerializer(serializers.ModelSerializer):
    def validate_logo(self, value):
        if value and value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("School logos must be 5 MB or smaller.")
        return value

    class Meta:
        model = School
        fields = ["id", "name", "slug", "registration_number", "email", "phone", "address", "logo", "education_systems", "status", "rejection_reason", "approved_at", "created_at"]
        read_only_fields = ["id", "slug", "status", "rejection_reason", "approved_at", "created_at"]


class SchoolSettingsSerializer(serializers.ModelSerializer):
    # Explicit list field so it works for both JSON and multipart (logo upload) requests.
    education_systems = serializers.ListField(child=serializers.CharField(), required=False)

    class Meta:
        model = School
        fields = ["name", "registration_number", "email", "phone", "address", "logo", "education_systems"]

    def validate_education_systems(self, value):
        return validate_education_systems(value)

    def validate_logo(self, value):
        if value and value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("School logos must be 5 MB or smaller.")
        return value
