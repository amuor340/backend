"""
Grading helpers shared by the results app.

The grade bands themselves live in ``schools.education`` (one place, no database
access). This module adds the two things that need the database or a result row:
finding the learner's education system and the editable ``GradeScale`` row.

Everything here is the single canonical implementation — ``results.services`` and
``dashboard.views`` import from this module instead of keeping their own copies.
"""
from decimal import Decimal, InvalidOperation

from schools import education

from .models import GradeScale


def to_decimal(value, default=Decimal("0")):
    """Safely convert a value to Decimal."""
    if value is None:
        return default
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return default


def calculate_percentage(marks, total_marks):
    """
    Convert marks to a percentage of the assessment's own total.

    40 / 50 -> 80.00     87 / 100 -> 87.00
    """
    if marks is None or total_marks is None:
        return Decimal("0")
    total = to_decimal(total_marks)
    if total <= 0:
        return Decimal("0")
    return ((to_decimal(marks) / total) * Decimal("100")).quantize(Decimal("0.01"))


def system_for_classroom(classroom):
    """Education system implied by a class's level (P4 -> South Sudan primary, ...)."""
    return education.system_for_level(getattr(classroom, "grade", None))


def calculate_cbc_grade(score, system=education.DEFAULT_SYSTEM):
    """
    (code, description) for a percentage under ``system``.

    The name is historical (it began as the Kenyan CBC level function); it now
    returns the right level for every supported system, e.g. EE1 / A- / B.
    """
    return education.performance_level(system, score)


def get_grade(score, system=education.DEFAULT_SYSTEM):
    """The editable GradeScale row matching a percentage within one system, if any."""
    if score is None:
        return None
    value = to_decimal(score)
    return (
        GradeScale.objects.filter(
            education_system=system,
            minimum_score__lte=value,
            maximum_score__gte=value,
        )
        .order_by("-minimum_score")
        .first()
    )


def school_header(school, request=None):
    """
    The school's identity block for printed documents (report cards, receipts).
    The school's own name leads every document; the platform name only appears
    in the footer.
    """
    if school is None:
        return None

    logo = None
    if school.logo:
        logo = request.build_absolute_uri(school.logo.url) if request else school.logo.url

    return {
        "id": school.id,
        "name": school.name,
        "logo": logo,
        "address": school.address,
        "phone": school.phone,
        "email": school.email,
        "registration_number": school.registration_number,
    }


def can_view_student(user, student):
    """Who may open a learner's academic documents."""
    role = getattr(user, "role", None)
    if role == "SUPER_ADMIN":
        return True
    if role == "PARENT":
        parent = getattr(student, "parent", None)
        return bool(parent and parent.user_id == user.id)
    if role == "STUDENT":
        return getattr(student, "user_id", None) == user.id
    return bool(user.school_id) and student.school_id == user.school_id


def education_summary(system):
    """What a report card needs to know about the grading system in use."""
    cfg = education.SYSTEMS.get(system, education.SYSTEMS[education.DEFAULT_SYSTEM])
    return {
        "key": system,
        "label": cfg["short_label"],
        "uses_points": cfg["uses_points"],
        "pass_mark": str(cfg["pass_mark"]),
        "bands": [
            {"code": b.code, "description": b.description, "minimum": str(b.minimum), "maximum": str(b.maximum)}
            for b in cfg["bands"]
        ],
    }
