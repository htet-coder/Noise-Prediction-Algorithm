# -*- coding: utf-8 -*-

import math
import unittest

from core.bs5228_engine import (
    GroundType,
    PredictionInput,
    ScreeningType,
    duration_correction,
    hard_ground_distance_attenuation,
    logarithmic_sum,
    predict_noise_level,
)


class TestBS5228Engine(unittest.TestCase):

    def test_hard_ground_at_10_metres(self):
        attenuation = hard_ground_distance_attenuation(10.0)
        self.assertAlmostEqual(attenuation, 0.0, places=6)

    def test_hard_ground_at_100_metres(self):
        attenuation = hard_ground_distance_attenuation(100.0)
        self.assertAlmostEqual(attenuation, 20.0, places=6)

    def test_half_duration(self):
        correction = duration_correction(
            activity_duration_hours=4.0,
            assessment_duration_hours=8.0,
        )
        self.assertAlmostEqual(correction, -3.0103, places=3)

    def test_equal_duration(self):
        correction = duration_correction(
            activity_duration_hours=8.0,
            assessment_duration_hours=8.0,
        )
        self.assertAlmostEqual(correction, 0.0, places=6)

    def test_two_equal_sources(self):
        combined = logarithmic_sum([60.0, 60.0])
        self.assertAlmostEqual(combined, 63.0103, places=3)

    def test_complete_prediction(self):
        data = PredictionInput(
            source_level_db=90.0,
            distance_m=100.0,
            ground_type=GroundType.HARD,
            screening_type=ScreeningType.FULL,
            reflection_correction_db=3.0,
            activity_duration_hours=4.0,
            assessment_duration_hours=8.0,
        )

        result = predict_noise_level(data)

        expected = (
            90.0
            - 20.0
            - 10.0
            + 3.0
            + 10.0 * math.log10(4.0 / 8.0)
        )

        self.assertAlmostEqual(
            result.predicted_level_db,
            expected,
            places=6,
        )

    def test_invalid_distance(self):
        with self.assertRaises(ValueError):
            hard_ground_distance_attenuation(0.0)

    def test_activity_exceeds_assessment_period(self):
        with self.assertRaises(ValueError):
            duration_correction(
                activity_duration_hours=10.0,
                assessment_duration_hours=8.0,
            )


if __name__ == "__main__":
    unittest.main()