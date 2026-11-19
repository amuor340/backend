from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models



class CustomUserManager(UserManager):
    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("role", "SUPER_ADMIN")
        extra_fields.setdefault("school", None)
        return super().create_superuser(username, email=email, password=password, **extra_fields)


class CustomUser(AbstractUser):
    objects = CustomUserManager()
    class Role(models.TextChoices):
        SUPER_ADMIN = "SUPER_ADMIN", "Platform Super Admin"
        SCHOOL_ADMIN = "SCHOOL_ADMIN", "School Administrator"
        ACADEMIC_COORDINATOR = "ACADEMIC_COORDINATOR", "Academic Coordinator"
        ACCOUNTANT = "ACCOUNTANT", "Accountant"
        TEACHER = "TEACHER", "Teacher"
        PARENT = "PARENT", "Parent"
        STUDENT = "STUDENT", "Student"


    role = models.CharField(
        max_length=30,
        choices=Role.choices,
        default=Role.STUDENT,
    )


    school = models.ForeignKey(
        "schools.School", on_delete=models.PROTECT, null=True, blank=True,
        related_name="users", db_index=True,
    )

    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
    )


    profile_picture = models.ImageField(
        upload_to="profile_pictures/",
        blank=True,
        null=True,
    )


    is_active = models.BooleanField(default=True)


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        ordering = ["first_name", "last_name", "username"]


    def __str__(self):
        full_name = self.get_full_name()
        return full_name if full_name else self.username



# ==========================================
# Parent Profile
# ==========================================
class ParentProfile(models.Model):
    school = models.ForeignKey("schools.School", on_delete=models.PROTECT, null=True, blank=True, related_name="parent_profiles", db_index=True)
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="parent_profile",
    )


    occupation = models.CharField(
        max_length=100,
        blank=True,
    )


    address = models.TextField(
        blank=True,
    )


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        ordering = ["user__first_name", "user__last_name"]


    def save(self, *args, **kwargs):
        if not self.school_id and self.user_id:
            self.school_id = self.user.school_id
        super().save(*args, **kwargs)

    def __str__(self):
        return self.user.get_full_name() or self.user.username



# ==========================================
# Teacher Profile
# ==========================================
class TeacherProfile(models.Model):
    school = models.ForeignKey("schools.School", on_delete=models.PROTECT, null=True, blank=True, related_name="teacher_profiles", db_index=True)

    class Gender(models.TextChoices):
        MALE = "Male", "Male"
        FEMALE = "Female", "Female"


    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="teacher_profile",
    )


    employee_number = models.CharField(
        max_length=30,
    )


    national_id = models.CharField(
        max_length=20,
    )


    gender = models.CharField(
        max_length=10,
        choices=Gender.choices,
    )


    date_of_birth = models.DateField()


    qualification = models.CharField(
        max_length=100,
    )


    employment_date = models.DateField()


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        ordering = ["employee_number"]
        constraints = [
            models.UniqueConstraint(fields=["school", "employee_number"], name="unique_school_teacher_employee_number"),
            models.UniqueConstraint(fields=["school", "national_id"], name="unique_school_teacher_national_id"),
        ]

    def save(self, *args, **kwargs):
        if not self.school_id and self.user_id:
            self.school_id = self.user.school_id
        super().save(*args, **kwargs)

    def __str__(self):
        return self.user.get_full_name() or self.user.username



# ==========================================
# Accountant Profile
# ==========================================
class AccountantProfile(models.Model):
    school = models.ForeignKey("schools.School", on_delete=models.PROTECT, null=True, blank=True, related_name="accountant_profiles", db_index=True)
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="accountant_profile",
    )


    employee_number = models.CharField(
        max_length=30,
    )


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        ordering = ["employee_number"]
        constraints = [models.UniqueConstraint(fields=["school", "employee_number"], name="unique_school_accountant_employee_number")]

    def save(self, *args, **kwargs):
        if not self.school_id and self.user_id:
            self.school_id = self.user.school_id
        super().save(*args, **kwargs)

    def __str__(self):
        return self.user.get_full_name() or self.user.username



# ==========================================
# Academic Coordinator Profile
# ==========================================
class AcademicCoordinatorProfile(models.Model):
    school = models.ForeignKey("schools.School", on_delete=models.PROTECT, null=True, blank=True, related_name="coordinator_profiles", db_index=True)
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="academic_coordinator_profile",
    )


    employee_number = models.CharField(
        max_length=30,
    )


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        ordering = ["employee_number"]
        constraints = [models.UniqueConstraint(fields=["school", "employee_number"], name="unique_school_coordinator_employee_number")]

    def save(self, *args, **kwargs):
        if not self.school_id and self.user_id:
            self.school_id = self.user.school_id
        super().save(*args, **kwargs)

    def __str__(self):
        return self.user.get_full_name() or self.user.username 


# ==========================================
# Student Profile — ✅ PHONE ADDED
# ==========================================
class StudentProfile(models.Model):
    school = models.ForeignKey("schools.School", on_delete=models.PROTECT, null=True, blank=True, related_name="student_profiles", db_index=True)

    class Gender(models.TextChoices):
        MALE = "Male", "Male"
        FEMALE = "Female", "Female"


    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="student_profile",
    )


    admission_number = models.CharField(
        max_length=30,
    )


    national_id = models.CharField(
        max_length=20,
        blank=True,
        null=True,
    )


    gender = models.CharField(
        max_length=10,
        choices=Gender.choices,
    )


    date_of_birth = models.DateField()

    # ✅ ADDED: Direct parent phone field on StudentProfile
    parent_phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Parent/Guardian phone number",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        ordering = ["admission_number"]
        constraints = [
            models.UniqueConstraint(fields=["school", "admission_number"], name="unique_school_student_profile_admission"),
            models.UniqueConstraint(fields=["school", "national_id"], name="unique_school_student_profile_national_id"),
        ]

    def save(self, *args, **kwargs):
        if not self.school_id and self.user_id:
            self.school_id = self.user.school_id
        super().save(*args, **kwargs)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


# ==========================================
# Password reset code (hashed, single use)
# ==========================================
class PasswordResetCode(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="password_reset_codes",
    )
    code_hash = models.CharField(max_length=255)
    attempts = models.PositiveSmallIntegerField(default=0)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["user", "-created_at"], name="pwreset_user_created_idx")]

    def __str__(self):
        return f"Reset code for {self.user_id} ({'used' if self.used_at else 'open'})"
