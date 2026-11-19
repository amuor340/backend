"""
Education systems supported by Pseudosphere.

This module is the single source of truth for:
  * which class levels belong to which curriculum,
  * how a percentage maps to a performance level / grade.

It is plain Python (no database access) so it can be imported anywhere
(models, serializers, services, management commands, tests).

A school chooses the systems it offers (``School.education_systems``). The
grading system used for a learner is derived from the level of their class,
so one school can run, for example, South Sudan primary (P1-P8) and
secondary (S1-S4) side by side.

Default grade bands are sensible national defaults. Schools can still edit
the bands stored in the ``results.GradeScale`` table; these values are used
to seed that table and as a fallback when a system has no rows there.
"""
from collections import namedtuple
from decimal import Decimal

KENYA_CBC = "KENYA_CBC"
KENYA_HIGH_SCHOOL = "KENYA_HIGH_SCHOOL"
SOUTH_SUDAN_PRIMARY = "SOUTH_SUDAN_PRIMARY"
SOUTH_SUDAN_SECONDARY = "SOUTH_SUDAN_SECONDARY"

DEFAULT_SYSTEM = KENYA_CBC

# code, description, minimum %, maximum %, points, remark
Band = namedtuple("Band", "code description minimum maximum points remark")

NOT_ASSESSED = ("N/A", "Not Assessed")


def _bands(rows):
    return tuple(
        Band(code, desc, Decimal(str(lo)), Decimal(str(hi)), pts, remark)
        for code, desc, lo, hi, pts, remark in rows
    )


_CBC_BANDS = _bands([
    ("EE1", "Exceeding Expectation", 90, 100, 8, "Outstanding mastery of the competencies."),
    ("EE2", "Exceeding Expectation", 75, 89.99, 7, "Very good — goes beyond what is expected."),
    ("ME1", "Meeting Expectation", 58, 74.99, 6, "Good — meets the expected competencies."),
    ("ME2", "Meeting Expectation", 41, 57.99, 5, "Fair — meets most expected competencies."),
    ("AE1", "Approaching Expectation", 31, 40.99, 4, "Nearly there — needs some support."),
    ("AE2", "Approaching Expectation", 21, 30.99, 3, "Needs regular support to reach expectations."),
    ("BE1", "Below Expectation", 11, 20.99, 2, "Needs significant support."),
    ("BE2", "Below Expectation", 1, 10.99, 1, "Needs intensive support."),
])

# Kenya secondary (8-4-4 / KCSE style 12-point scale)
_KENYA_HS_BANDS = _bands([
    ("A", "Excellent", 80, 100, 12, "Excellent performance."),
    ("A-", "Very Good", 75, 79.99, 11, "Very good performance."),
    ("B+", "Very Good", 70, 74.99, 10, "Very good performance."),
    ("B", "Good", 65, 69.99, 9, "Good performance."),
    ("B-", "Good", 60, 64.99, 8, "Good performance."),
    ("C+", "Satisfactory", 55, 59.99, 7, "Satisfactory — keep improving."),
    ("C", "Satisfactory", 50, 54.99, 6, "Average performance."),
    ("C-", "Fair", 45, 49.99, 5, "Fair — more effort needed."),
    ("D+", "Weak", 40, 44.99, 4, "Weak — needs consistent revision."),
    ("D", "Weak", 35, 39.99, 3, "Weak — needs support."),
    ("D-", "Poor", 30, 34.99, 2, "Poor — needs urgent support."),
    ("E", "Very Poor", 0, 29.99, 1, "Very poor — immediate intervention needed."),
])

# South Sudan Certificate of Secondary Education scale (national exam bands).
_SOUTH_SUDAN_BANDS = _bands([
    ("A", "Excellent", 75, 100, 4, "Excellent performance."),
    ("B", "Very Good", 60, 74.99, 3, "Very good performance."),
    ("C", "Good", 45, 59.99, 2, "Good — satisfactory performance."),
    ("D", "Pass", 31, 44.99, 1, "Pass — needs improvement."),
    ("F", "Fail", 0, 30.99, 0, "Fail — below the pass mark."),
])


def _levels(prefix, start, end):
    return [f"{prefix}{n}" for n in range(start, end + 1)]


SYSTEMS = {
    KENYA_CBC: {
        "label": "Kenya — Competency Based Curriculum (Day Care to Grade 9)",
        "short_label": "CBC",
        "country": "Kenya",
        "levels": ["Day Care", "PP1", "PP2"] + [f"Grade {n}" for n in range(1, 10)],
        "bands": _CBC_BANDS,
        "uses_points": False,
        "pass_mark": Decimal("41"),
        "terms": 3,
    },
    KENYA_HIGH_SCHOOL: {
        "label": "Kenya — High School (Form 1 to Form 4)",
        "short_label": "High School",
        "country": "Kenya",
        "levels": [f"Form {n}" for n in range(1, 5)],
        "bands": _KENYA_HS_BANDS,
        "uses_points": True,
        "pass_mark": Decimal("30"),
        "terms": 3,
    },
    SOUTH_SUDAN_PRIMARY: {
        "label": "South Sudan — Primary (P1 to P8)",
        "short_label": "South Sudan Primary",
        "country": "South Sudan",
        "levels": _levels("P", 1, 8),
        "bands": _SOUTH_SUDAN_BANDS,
        "uses_points": False,
        "pass_mark": Decimal("31"),
        "terms": 3,
    },
    SOUTH_SUDAN_SECONDARY: {
        "label": "South Sudan — Secondary (S1 to S4)",
        "short_label": "South Sudan Secondary",
        "country": "South Sudan",
        "levels": _levels("S", 1, 4),
        "bands": _SOUTH_SUDAN_BANDS,
        "uses_points": True,
        "pass_mark": Decimal("31"),
        "terms": 3,
    },
}

SYSTEM_CHOICES = [(key, cfg["label"]) for key, cfg in SYSTEMS.items()]

# Every selectable class level, in curriculum order, as Django choices.
LEVEL_CHOICES = [(level, level) for cfg in SYSTEMS.values() for level in cfg["levels"]]

_LEVEL_TO_SYSTEM = {level: key for key, cfg in SYSTEMS.items() for level in cfg["levels"]}


def is_valid_system(system):
    return system in SYSTEMS


def system_for_level(level, default=DEFAULT_SYSTEM):
    """Return the education system a class level (e.g. 'P4', 'Form 2') belongs to."""
    return _LEVEL_TO_SYSTEM.get((level or "").strip(), default)


def levels_for_systems(systems):
    """Class levels available to a school offering the given systems."""
    chosen = [s for s in (systems or [DEFAULT_SYSTEM]) if s in SYSTEMS]
    return [level for s in chosen for level in SYSTEMS[s]["levels"]]


def bands_for(system):
    return SYSTEMS.get(system, SYSTEMS[DEFAULT_SYSTEM])["bands"]


def band_for_score(system, score):
    """Return the Band matching a percentage, or None when not assessed (<= 0 for CBC)."""
    try:
        value = Decimal(str(score))
    except Exception:
        return None
    value = min(max(value, Decimal("0")), Decimal("100"))
    for band in bands_for(system):
        if band.minimum <= value <= band.maximum:
            return band
    # Values between two published bands (e.g. 74.995) fall to the highest band below them.
    for band in bands_for(system):
        if value >= band.minimum:
            return band
    return None


def performance_level(system, score):
    """(code, description) for a percentage under the given system."""
    band = band_for_score(system, score)
    return (band.code, band.description) if band else NOT_ASSESSED


def points_for(system, score):
    band = band_for_score(system, score)
    return band.points if band else 0


def system_catalog():
    """Serializable description of every system (used by the API / frontend)."""
    return [
        {
            "key": key,
            "label": cfg["label"],
            "short_label": cfg["short_label"],
            "country": cfg["country"],
            "levels": cfg["levels"],
            "uses_points": cfg["uses_points"],
            "pass_mark": str(cfg["pass_mark"]),
            "bands": [
                {
                    "code": b.code,
                    "description": b.description,
                    "minimum": str(b.minimum),
                    "maximum": str(b.maximum),
                    "points": b.points,
                }
                for b in cfg["bands"]
            ],
        }
        for key, cfg in SYSTEMS.items()
    ]


# Starter subjects a school can create in one click for each system.
STARTER_SUBJECTS = {
    KENYA_CBC: [
        ("English", "ENG"), ("Kiswahili", "KIS"), ("Mathematics", "MAT"),
        ("Integrated Science", "SCI"), ("Social Studies", "SST"),
        ("Creative Arts", "ART"), ("Religious Education", "RE"),
        ("Agriculture & Nutrition", "AGN"), ("Physical & Health Education", "PHE"),
    ],
    KENYA_HIGH_SCHOOL: [
        ("English", "ENG"), ("Kiswahili", "KIS"), ("Mathematics", "MAT"),
        ("Biology", "BIO"), ("Chemistry", "CHE"), ("Physics", "PHY"),
        ("History & Government", "HIS"), ("Geography", "GEO"),
        ("Christian Religious Education", "CRE"), ("Business Studies", "BST"),
        ("Computer Studies", "CMP"),
    ],
    SOUTH_SUDAN_PRIMARY: [
        ("English", "ENG"), ("Mathematics", "MAT"), ("Science", "SCI"),
        ("Social Studies", "SST"), ("Religious Education", "RE"),
        ("Arabic", "ARA"), ("Local Language", "LOC"),
        ("Physical Education", "PE"), ("Creative Arts", "ART"),
    ],
    SOUTH_SUDAN_SECONDARY: [
        ("English", "ENG"), ("Mathematics", "MAT"), ("Biology", "BIO"),
        ("Chemistry", "CHE"), ("Physics", "PHY"), ("History", "HIS"),
        ("Geography", "GEO"), ("Religious Education", "RE"),
        ("Commerce", "COM"), ("Computer Studies", "CMP"),
    ],
}
