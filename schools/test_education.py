"""Pure-Python tests for the grading engine (no database needed)."""
from decimal import Decimal
from unittest import TestCase

from schools import education as edu


def legacy_cbc(score):
    for threshold, code in [(90, "EE1"), (75, "EE2"), (58, "ME1"), (41, "ME2"),
                            (31, "AE1"), (21, "AE2"), (11, "BE1"), (1, "BE2")]:
        if float(score) >= threshold:
            return code
    return "N/A"


class GradingEngineTests(TestCase):
    def test_cbc_matches_the_original_hard_coded_scale_for_every_score(self):
        for i in range(0, 10001):
            score = Decimal(i) / 100
            self.assertEqual(edu.performance_level(edu.KENYA_CBC, score)[0], legacy_cbc(score), score)

    def test_kenya_high_school_boundaries(self):
        cases = [(100, "A"), (80, "A"), (79.99, "A-"), (65, "B"), (44.99, "D+"), (30, "D-"), (29.99, "E"), (0, "E")]
        for score, expected in cases:
            self.assertEqual(edu.performance_level(edu.KENYA_HIGH_SCHOOL, score)[0], expected, score)

    def test_south_sudan_boundaries(self):
        cases = [(100, "A"), (75, "A"), (74.99, "B"), (60, "B"), (45, "C"), (31, "D"), (30.99, "F"), (0, "F")]
        for system in (edu.SOUTH_SUDAN_PRIMARY, edu.SOUTH_SUDAN_SECONDARY):
            for score, expected in cases:
                self.assertEqual(edu.performance_level(system, score)[0], expected, (system, score))

    def test_non_cbc_systems_have_no_gaps_or_overlaps(self):
        for system in (edu.KENYA_HIGH_SCHOOL, edu.SOUTH_SUDAN_PRIMARY, edu.SOUTH_SUDAN_SECONDARY):
            for i in range(0, 10001):
                value = Decimal(i) / 100
                matches = [b for b in edu.bands_for(system) if b.minimum <= value <= b.maximum]
                self.assertEqual(len(matches), 1, (system, value))

    def test_levels_map_to_their_system_and_are_unique(self):
        self.assertEqual(edu.system_for_level("P8"), edu.SOUTH_SUDAN_PRIMARY)
        self.assertEqual(edu.system_for_level("S4"), edu.SOUTH_SUDAN_SECONDARY)
        self.assertEqual(edu.system_for_level("Form 3"), edu.KENYA_HIGH_SCHOOL)
        self.assertEqual(edu.system_for_level("Grade 6"), edu.KENYA_CBC)
        levels = [level for level, _ in edu.LEVEL_CHOICES]
        self.assertEqual(len(levels), len(set(levels)))

    def test_levels_for_systems(self):
        both = edu.levels_for_systems([edu.SOUTH_SUDAN_PRIMARY, edu.SOUTH_SUDAN_SECONDARY])
        self.assertEqual(both[0], "P1")
        self.assertIn("S4", both)
        self.assertNotIn("Grade 1", both)
