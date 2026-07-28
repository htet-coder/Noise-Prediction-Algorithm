from dataclasses import dataclass
from typing import Any


@dataclass
class SourceModel:
    """
    Represents one noise source and its source-specific activity attributes.
    """

    feature_id: int
    source_id: str
    activity: str
    equipment: str
    level_db: float
    duration_hours: float
    ground_type: str
    screening: str
    reflection_db: float
    geometry: Any

    def duration_correction_db(self, reference_hours: float = 12.0) -> float:
        """
        Returns the operating-time correction relative to the reference period.

        A source operating for the full reference period receives 0 dB.
        Shorter durations receive a negative correction.
        """
        import math

        if reference_hours <= 0:
            raise ValueError("Reference duration must be greater than zero.")

        if self.duration_hours <= 0:
            raise ValueError(
                f"Source {self.source_id} has an invalid operating duration."
            )

        return 10.0 * math.log10(self.duration_hours / reference_hours)

    def validate(self) -> list[str]:
        """
        Returns validation messages for this source.
        An empty list means the source is valid.
        """
        errors = []

        if not self.source_id.strip():
            errors.append("Source ID is missing.")

        if not self.activity.strip():
            errors.append("Activity is missing.")

        if not self.equipment.strip():
            errors.append("Equipment is missing.")

        if not 0.0 <= self.level_db <= 200.0:
            errors.append("Noise level must be between 0 and 200 dB.")

        if self.duration_hours <= 0:
            errors.append("Operating duration must be greater than zero.")

        if self.reflection_db < 0:
            errors.append("Reflection correction cannot be negative.")

        valid_ground_types = {
            "hard",
            "soft",
            "mixed",
        }

        if self.ground_type.strip().lower() not in valid_ground_types:
            errors.append(
                "Ground type must be Hard, Soft, or Mixed."
            )

        valid_screening_types = {
            "none",
            "partial",
            "full",
        }

        if self.screening.strip().lower() not in valid_screening_types:
            errors.append(
                "Screening must be None, Partial, or Full."
            )

        return errors