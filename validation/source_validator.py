from dataclasses import dataclass, field
from typing import Iterable, List

from ..models.source_model import SourceModel


@dataclass
class ValidationIssue:
    """
    Represents one validation issue for one source.
    """

    source_id: str
    message: str
    severity: str = "error"

    def __post_init__(self) -> None:
        allowed = {"error", "warning"}

        if self.severity not in allowed:
            raise ValueError(
                f"Unsupported validation severity: {self.severity}"
            )


@dataclass
class ValidationReport:
    """
    Stores validation results for a collection of noise sources.
    """

    total_sources: int = 0
    valid_sources: int = 0
    issues: List[ValidationIssue] = field(default_factory=list)

    @property
    def error_count(self) -> int:
        return sum(
            1 for issue in self.issues
            if issue.severity == "error"
        )

    @property
    def warning_count(self) -> int:
        return sum(
            1 for issue in self.issues
            if issue.severity == "warning"
        )

    @property
    def is_valid(self) -> bool:
        return self.error_count == 0

    def add_error(self, source_id: str, message: str) -> None:
        self.issues.append(
            ValidationIssue(
                source_id=source_id,
                message=message,
                severity="error",
            )
        )

    def add_warning(self, source_id: str, message: str) -> None:
        self.issues.append(
            ValidationIssue(
                source_id=source_id,
                message=message,
                severity="warning",
            )
        )

    def to_text(self) -> str:
        """
        Returns a readable validation summary for the GUI.
        """
        lines = [
            "Source Validation Summary",
            "",
            f"Total sources: {self.total_sources}",
            f"Valid sources: {self.valid_sources}",
            f"Errors: {self.error_count}",
            f"Warnings: {self.warning_count}",
        ]

        if not self.issues:
            lines.extend(
                [
                    "",
                    "No validation issues were found.",
                ]
            )
            return "\n".join(lines)

        lines.extend(["", "Issues:"])

        for issue in self.issues:
            label = issue.severity.upper()
            lines.append(
                f"[{label}] {issue.source_id}: {issue.message}"
            )

        return "\n".join(lines)


class SourceValidator:
    """
    Validates source-specific Phase 4C activity attributes.
    """

    def validate(
        self,
        sources: Iterable[SourceModel],
        source_specific_mode: bool = False,
    ) -> ValidationReport:
        """
        Validate calculation-critical source values.

        Activity and equipment are not required in Simple mode. In
        Source-Specific mode, missing descriptive metadata is reported as a
        warning and does not prevent the prediction from running.
        """
        source_list = list(sources)

        report = ValidationReport(
            total_sources=len(source_list)
        )

        if not source_list:
            report.add_error(
                "General",
                "No source features were supplied.",
            )
            return report

        seen_ids = set()

        for source in source_list:
            source_errors_before = report.error_count
            display_id = source.source_id or str(source.feature_id)

            if source.source_id in seen_ids:
                report.add_warning(
                    display_id,
                    "Duplicate source ID.",
                )
            else:
                seen_ids.add(source.source_id)

            for message in source.validate():
                report.add_error(display_id, message)

            if source_specific_mode:
                if not str(source.activity or "").strip():
                    report.add_warning(
                        display_id,
                        "Activity is not specified.",
                    )
                if not str(source.equipment or "").strip():
                    report.add_warning(
                        display_id,
                        "Equipment is not specified.",
                    )

            if source.geometry is None:
                report.add_error(
                    display_id,
                    "Source geometry is missing.",
                )

            if source.duration_hours > 24.0:
                report.add_warning(
                    display_id,
                    "Operating duration is greater than 24 hours.",
                )

            if source.reflection_db > 10.0:
                report.add_warning(
                    display_id,
                    "Reflection correction is unusually high.",
                )

            if report.error_count == source_errors_before:
                report.valid_sources += 1

        return report