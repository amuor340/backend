from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as DjangoValidationError


from .validators import validate_profile_image
from .models import (
    ParentProfile,
    TeacherProfile,
    AccountantProfile,
    AcademicCoordinatorProfile,
    StudentProfile,
)


User = get_user_model()



# ============================================================
# User Serializer
# ============================================================


class UserSerializer(serializers.ModelSerializer):


    # ========================================================
    # Whether this user's role-specific profile exists.
    #
    # SUPER_ADMIN has no separate profile model by design,
    # so it is always considered to have a profile.
    # ========================================================


    has_profile = serializers.SerializerMethodField()
    school_name = serializers.SerializerMethodField()


    class Meta:
        model = User


        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "role",
            "school",
            "school_name",
            "profile_picture",
            "is_active",
            "has_profile",
            "created_at",
        ]


        read_only_fields = [
            "id",
            "school",
            "has_profile",
            "created_at",
        ]


    def get_school_name(self, obj):
        return obj.school.name if obj.school_id else ""

    def validate_profile_picture(self, value):
        try:
            return validate_profile_image(value)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(list(exc.messages))

    def get_has_profile(self, obj):


        profile_attr = {
            "PARENT": "parent_profile",
            "TEACHER": "teacher_profile",
            "ACCOUNTANT": "accountant_profile",
            "ACADEMIC_COORDINATOR": (
                "academic_coordinator_profile"
            ),
            "STUDENT": "student_profile",
        }.get(obj.role)


        # Platform and school administrators do not have separate profile models.
        if not profile_attr:
            return True


        return hasattr(obj, profile_attr)



# ============================================================
# Registration Serializer
# ============================================================


class RegisterSerializer(serializers.ModelSerializer):


    password = serializers.CharField(
        write_only=True,
        min_length=8,
    )


    class Meta:
        model = User


        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "password",
            "role",
            "profile_picture",
        ]
        extra_kwargs = {
            "profile_picture": {"required": False, "allow_null": True},
        }


    def validate_profile_picture(self, value):
        try:
            return validate_profile_image(value)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(list(exc.messages))


    def validate(self, attrs):
        # A photo is optional for staff and parents (they can add it later from
        # their profile) but mandatory when registering a student.
        if attrs.get("role") == User.Role.STUDENT and not attrs.get("profile_picture"):
            raise serializers.ValidationError(
                {"profile_picture": "A profile picture is required to register a student."}
            )
        return attrs


    def create(self, validated_data):
        password = validated_data.pop("password")
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError({"detail": "Authenticated registration is required."})

        if request.user.role == User.Role.SCHOOL_ADMIN:
            allowed_roles = {
                User.Role.TEACHER,
                User.Role.PARENT,
                User.Role.STUDENT,
                User.Role.ACCOUNTANT,
                User.Role.ACADEMIC_COORDINATOR,
            }
            if validated_data.get("role") not in allowed_roles:
                raise serializers.ValidationError({"role": "You cannot create this role."})
            if not request.user.school_id:
                raise serializers.ValidationError({"school": "Your account is not assigned to a school."})
            validated_data["school"] = request.user.school
        elif request.user.role == User.Role.SUPER_ADMIN:
            if validated_data.get("role") != User.Role.SCHOOL_ADMIN:
                raise serializers.ValidationError({"role": "Platform Super Admin can create School Admin accounts only through this endpoint."})
            # A school must be assigned explicitly by the school onboarding/approval workflow.
            validated_data["school"] = None
        else:
            raise serializers.ValidationError({"detail": "You do not have permission to register users."})

        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user



# ============================================================
# Parent Profile Serializer
# ============================================================


class ParentProfileSerializer(serializers.ModelSerializer):


    user = UserSerializer(
        read_only=True
    )


    # Parent user ID
    parent_user_id = serializers.IntegerField(
        source="user.id",
        read_only=True,
    )


    # Parent display name
    parent_name = serializers.SerializerMethodField()


    # Parent phone
    parent_phone = serializers.CharField(
        source="user.phone_number",
        read_only=True,
    )


    # First / primary student ID
    student_id = serializers.SerializerMethodField()


    # All students belonging to this parent
    student_ids = serializers.SerializerMethodField()


    # Student details
    children = serializers.SerializerMethodField()


    def get_parent_name(self, obj):


        if obj.user:


            full_name = (
                f"{obj.user.first_name or ''} "
                f"{obj.user.last_name or ''}"
            ).strip()


            return (
                full_name
                or obj.user.username
            )


        return ""


    def get_student_id(self, obj):
        """
        Return the first linked student's ID.


        Useful when the parent has one child.
        """


        try:


            students = obj.children.all()


            first_student = students.first()


            if first_student:
                return first_student.id


        except Exception:
            pass


        return None


    def get_student_ids(self, obj):
        """
        Return IDs of ALL students linked to this parent.
        """


        try:


            return list(
                obj.children.values_list(
                    "id",
                    flat=True,
                )
            )


        except Exception:
            return []


    def get_children(self, obj):
        """
        Return useful information about every child.
        """


        try:


            students = obj.children.all()


            return [
                {
                    "id": student.id,


                    "student_id": student.id,


                    "admission_number": getattr(
                        student,
                        "admission_number",
                        getattr(
                            student,
                            "admission_no",
                            None,
                        ),
                    ),


                    "name": (
                        getattr(
                            student,
                            "name",
                            None,
                        )
                        or
                        (
                            f"{getattr(student, 'first_name', '')} "
                            f"{getattr(student, 'last_name', '')}"
                        ).strip()
                    ),
                }
                for student in students
            ]


        except Exception:
            return []


    class Meta:
        model = ParentProfile


        fields = [
            "id",
            "user",


            # Parent information
            "parent_user_id",
            "parent_name",
            "parent_phone",


            # Parent profile
            "occupation",
            "address",


            # Student relationship
            "student_id",
            "student_ids",
            "children",


            "created_at",
            "updated_at",
        ]


        read_only_fields = [
            "id",
            "user",
            "parent_user_id",
            "parent_name",
            "parent_phone",
            "student_id",
            "student_ids",
            "children",
            "created_at",
            "updated_at",
        ]



# ============================================================
# Teacher Profile Serializer
#
# Full serializer.
#
# Used for:
# - Teacher's own profile
# - Admin / Academic Coordinator views
#
# Sensitive fields such as national_id and date_of_birth
# are included here.
# ============================================================


class TeacherProfileSerializer(
    serializers.ModelSerializer
):


    user = UserSerializer(
        read_only=True
    )


    class Meta:
        model = TeacherProfile
        fields = "__all__"
        read_only_fields = ["school"]



# ============================================================
# Teacher Profile Public Serializer
#
# Used for dropdowns and cross-role listings where basic
# teacher information is required.
#
# Sensitive fields are deliberately excluded.
# ============================================================


class TeacherProfilePublicSerializer(
    serializers.ModelSerializer
):


    user = UserSerializer(
        read_only=True
    )


    class Meta:
        model = TeacherProfile


        fields = [
            "id",
            "user",
            "employee_number",
            "gender",
            "qualification",
            "employment_date",
        ]



# ============================================================
# Accountant Profile Serializer
# ============================================================


class AccountantProfileSerializer(
    serializers.ModelSerializer
):


    user = UserSerializer(
        read_only=True
    )


    class Meta:
        model = AccountantProfile
        fields = "__all__"
        read_only_fields = ["school"]



# ============================================================
# Academic Coordinator Serializer
# ============================================================


class AcademicCoordinatorProfileSerializer(
    serializers.ModelSerializer
):


    user = UserSerializer(
        read_only=True
    )


    class Meta:
        model = AcademicCoordinatorProfile
        fields = "__all__"
        read_only_fields = ["school"]



# ============================================================
# Student Profile Serializer — ✅ UPDATED WITH PARENT PHONE
# ============================================================


class StudentProfileSerializer(
    serializers.ModelSerializer
):


    user = UserSerializer(
        read_only=True
    )

    # ✅ PARENT PHONE — Automatically pulled from linked ParentProfile
    parent_phone = serializers.SerializerMethodField()

    def get_parent_phone(self, obj):
        """
        Get parent's phone number through the parent relationship.
        Assumes StudentProfile has a 'parent' ForeignKey to ParentProfile.
        """
        try:
            # If StudentProfile has 'parent' field → use it
            if hasattr(obj, "parent") and obj.parent:
                # Phone is stored on CustomUser → parent.user.phone_number
                return getattr(obj.parent.user, "phone_number", None)
        except Exception:
            pass
        return None


    class Meta:
        model = StudentProfile


        fields = [
            "id",
            "user",
            "admission_number",
            "national_id",
            "gender",
            "date_of_birth",
            "parent_phone",  # ✅ NOW INCLUDED!
            "created_at",
            "updated_at",
        ]


        read_only_fields = [
            "id",
            "user",
            "parent_phone",  # ✅ Read-only — auto-computed
            "created_at",
            "updated_at",
        ]