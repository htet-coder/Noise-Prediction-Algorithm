# -*- coding: utf-8 -*-
"""
Core noise calculation functions for the Noise Prediction QGIS plugin.

The functions in this module do not depend on QGIS. This allows the
calculations to be tested independently from the GUI and GIS workflow.

Current implementation preserves the principal calculation behaviour of
the original plugin while providing cleaner validation and outputs.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from typing import Iterable


class GroundType(str, Enum):
    """Supported simplified ground conditions."""

    HARD = "hard"
    SOFT = "soft"
    MIXED = "mixed"


class ScreeningType(str, Enum):
    """Simplified screening conditions used by the current plugin."""

    NONE = "none"
    PARTIAL = "partial"
    FULL = "full"


@dataclass(frozen=True)
class PredictionInput:
    """Inputs for one source-to-receptor noise calculation."""

    source_level_db: float
    distance_m: float

    ground_type: GroundType = GroundType.HARD
    soft_ground_percent: float = 0.0

    screening_type: ScreeningType = ScreeningType.NONE
    reflection_correction_db: float = 0.0

    activity_duration_hours: float = 1.0
    assessment_duration_hours: float = 1.0


@dataclass(frozen=True)
class PredictionResult:
    """Detailed and auditable calculation result."""

    source_level_db: float
    distance_m: float

    distance_attenuation_db: float
    ground_attenuation_db: float
    screening_attenuation_db: float
    reflection_correction_db: float
    duration_correction_db: float

    level_before_duration_db: float
    predicted_level_db: float


def validate_distance(distance_m: float) -> None:
    """Validate source-to-receptor distance."""

    if not math.isfinite(distance_m):
        raise ValueError("Distance must be a finite number.")

    if distance_m <= 0:
        raise ValueError("Distance must be greater than zero metres.")


def validate_percentage(value: float, name: str = "Percentage") -> None:
    """Validate a percentage between 0 and 100."""

    if not math.isfinite(value):
        raise ValueError(f"{name} must be a finite number.")

    if not 0 <= value <= 100:
        raise ValueError(f"{name} must be between 0 and 100.")


def hard_ground_distance_attenuation(distance_m: float) -> float:
    """
    Calculate hard-ground distance attenuation.

    Preserves the original plugin formula:

        20 × log10(distance / 10)

    The source level is therefore treated as a level referenced at 10 metres.
    """

    validate_distance(distance_m)
    return 20.0 * math.log10(distance_m / 10.0)


def soft_ground_distance_attenuation(distance_m: float) -> float:
    """
    Calculate soft-ground distance attenuation.

    Preserves the original plugin formula:

        25 × log10(distance / 10) - 2
    """

    validate_distance(distance_m)
    return 25.0 * math.log10(distance_m / 10.0) - 2.0


def mixed_ground_attenuation(
    distance_m: float,
    soft_ground_percent: float,
) -> float:
    """
    Calculate the additional attenuation for mixed ground.

    The original plugin calculates the difference between the soft-ground
    and hard-ground formulas and multiplies it by the soft-ground proportion.

    A value of 0% produces no additional ground attenuation.
    A value of 100% produces the complete soft-versus-hard difference.
    """

    validate_distance(distance_m)
    validate_percentage(soft_ground_percent, "Soft-ground percentage")

    hard_attenuation = hard_ground_distance_attenuation(distance_m)
    soft_attenuation = soft_ground_distance_attenuation(distance_m)

    difference = soft_attenuation - hard_attenuation
    proportion = soft_ground_percent / 100.0

    return proportion * difference


def calculate_distance_and_ground(
    distance_m: float,
    ground_type: GroundType,
    soft_ground_percent: float = 0.0,
) -> tuple[float, float]:
    """
    Return distance attenuation and separate ground attenuation.

    This separation is useful for reporting and auditing.
    """

    validate_distance(distance_m)

    if ground_type == GroundType.HARD:
        return hard_ground_distance_attenuation(distance_m), 0.0

    if ground_type == GroundType.SOFT:
        return soft_ground_distance_attenuation(distance_m), 0.0

    if ground_type == GroundType.MIXED:
        distance_attenuation = hard_ground_distance_attenuation(distance_m)
        ground_attenuation = mixed_ground_attenuation(
            distance_m=distance_m,
            soft_ground_percent=soft_ground_percent,
        )
        return distance_attenuation, ground_attenuation

    raise ValueError(f"Unsupported ground type: {ground_type}")


def screening_attenuation(screening_type: ScreeningType) -> float:
    """
    Return simplified screening attenuation.

    Current mapping:

        none    = 0 dB
        partial = 5 dB
        full    = 10 dB

    These values preserve the simplified logic used in the old plugin.
    """

    values = {
        ScreeningType.NONE: 0.0,
        ScreeningType.PARTIAL: 5.0,
        ScreeningType.FULL: 10.0,
    }

    try:
        return values[screening_type]
    except KeyError as exc:
        raise ValueError(
            f"Unsupported screening type: {screening_type}"
        ) from exc


def duration_correction(
    activity_duration_hours: float,
    assessment_duration_hours: float,
) -> float:
    """
    Calculate activity-duration correction logarithmically.

    Formula:

        correction = 10 × log10(activity duration / assessment duration)

    The result is zero or negative.

    Examples:
        8 hours during an 8-hour period = 0 dB
        4 hours during an 8-hour period ≈ -3 dB
        2 hours during an 8-hour period ≈ -6 dB
    """

    if activity_duration_hours <= 0:
        raise ValueError(
            "Activity duration must be greater than zero hours."
        )

    if assessment_duration_hours <= 0:
        raise ValueError(
            "Assessment duration must be greater than zero hours."
        )

    if activity_duration_hours > assessment_duration_hours:
        raise ValueError(
            "Activity duration cannot exceed the assessment duration."
        )

    ratio = activity_duration_hours / assessment_duration_hours
    return 10.0 * math.log10(ratio)


def predict_noise_level(data: PredictionInput) -> PredictionResult:
    """
    Calculate the predicted level for one source and one receptor.

    Calculation:

        predicted level
        = source level
        - distance attenuation
        - ground attenuation
        - screening attenuation
        + reflection correction
        + duration correction

    Duration correction is already negative when activity time is shorter
    than the assessment period.
    """

    distance_attenuation, ground_attenuation = (
        calculate_distance_and_ground(
            distance_m=data.distance_m,
            ground_type=data.ground_type,
            soft_ground_percent=data.soft_ground_percent,
        )
    )

    screen_attenuation = screening_attenuation(
        data.screening_type
    )

    time_correction = duration_correction(
        activity_duration_hours=data.activity_duration_hours,
        assessment_duration_hours=data.assessment_duration_hours,
    )

    level_before_duration = (
        data.source_level_db
        - distance_attenuation
        - ground_attenuation
        - screen_attenuation
        + data.reflection_correction_db
    )

    predicted_level = level_before_duration + time_correction

    return PredictionResult(
        source_level_db=data.source_level_db,
        distance_m=data.distance_m,
        distance_attenuation_db=distance_attenuation,
        ground_attenuation_db=ground_attenuation,
        screening_attenuation_db=screen_attenuation,
        reflection_correction_db=data.reflection_correction_db,
        duration_correction_db=time_correction,
        level_before_duration_db=level_before_duration,
        predicted_level_db=predicted_level,
    )


def logarithmic_sum(levels_db: Iterable[float]) -> float:
    """
    Combine multiple independent noise levels logarithmically.

    Formula:

        10 × log10(sum(10 ** (level / 10)))
    """

    levels = list(levels_db)

    if not levels:
        raise ValueError("At least one noise level is required.")

    if any(not math.isfinite(level) for level in levels):
        raise ValueError("All noise levels must be finite numbers.")

    energy_sum = sum(10.0 ** (level / 10.0) for level in levels)

    return 10.0 * math.log10(energy_sum)


def round_result(
    result: PredictionResult,
    decimals: int = 2,
) -> PredictionResult:
    """Return a rounded copy of a prediction result."""

    return PredictionResult(
        source_level_db=round(result.source_level_db, decimals),
        distance_m=round(result.distance_m, decimals),
        distance_attenuation_db=round(
            result.distance_attenuation_db, decimals
        ),
        ground_attenuation_db=round(
            result.ground_attenuation_db, decimals
        ),
        screening_attenuation_db=round(
            result.screening_attenuation_db, decimals
        ),
        reflection_correction_db=round(
            result.reflection_correction_db, decimals
        ),
        duration_correction_db=round(
            result.duration_correction_db, decimals
        ),
        level_before_duration_db=round(
            result.level_before_duration_db, decimals
        ),
        predicted_level_db=round(
            result.predicted_level_db, decimals
        ),
    )