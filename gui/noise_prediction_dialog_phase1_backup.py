# -*- coding: utf-8 -*-
"""
Basic BS 5228 noise calculation dialog.

This first GUI prototype calculates the predicted noise level for one
source and one receptor. GIS layers and map outputs will be added later.
"""

from __future__ import annotations

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QFont
from qgis.PyQt.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from ..core.bs5228_engine import (
    GroundType,
    PredictionInput,
    ScreeningType,
    predict_noise_level,
    round_result,
)


class NoisePredictionDialog(QDialog):
    """Main dialog for the new noise prediction GUI."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Noise Prediction — BS 5228")
        self.setMinimumWidth(620)
        self.resize(680, 720)

        self._build_ui()
        self._connect_signals()
        self._update_ground_controls()
        self._clear_results()

    def _build_ui(self) -> None:
        """Create all interface widgets."""

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(12)

        title_label = QLabel("Construction Noise Prediction")
        title_font = QFont()
        title_font.setPointSize(15)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)

        subtitle_label = QLabel(
            "Preliminary single source-to-receptor calculation"
        )
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setWordWrap(True)

        main_layout.addWidget(title_label)
        main_layout.addWidget(subtitle_label)

        input_group = QGroupBox("Prediction inputs")
        input_form = QFormLayout(input_group)
        input_form.setFieldGrowthPolicy(
            QFormLayout.AllNonFixedFieldsGrow
        )

        self.source_level_spin = self._create_double_spinbox(
            minimum=0.0,
            maximum=200.0,
            value=90.0,
            decimals=1,
            suffix=" dB",
        )
        self.source_level_spin.setToolTip(
            "Noise level for the activity or plant at the reference distance."
        )

        self.distance_spin = self._create_double_spinbox(
            minimum=0.1,
            maximum=1000000.0,
            value=100.0,
            decimals=1,
            suffix=" m",
        )

        self.ground_combo = QComboBox()
        self.ground_combo.addItem(
            "Hard ground",
            GroundType.HARD,
        )
        self.ground_combo.addItem(
            "Soft ground",
            GroundType.SOFT,
        )
        self.ground_combo.addItem(
            "Mixed ground",
            GroundType.MIXED,
        )

        self.soft_ground_spin = self._create_double_spinbox(
            minimum=0.0,
            maximum=100.0,
            value=50.0,
            decimals=1,
            suffix=" %",
        )

        self.screening_combo = QComboBox()
        self.screening_combo.addItem(
            "No screening — 0 dB",
            ScreeningType.NONE,
        )
        self.screening_combo.addItem(
            "Partial screening — 5 dB",
            ScreeningType.PARTIAL,
        )
        self.screening_combo.addItem(
            "Full screening — 10 dB",
            ScreeningType.FULL,
        )

        self.reflection_spin = self._create_double_spinbox(
            minimum=0.0,
            maximum=20.0,
            value=0.0,
            decimals=1,
            suffix=" dB",
        )
        self.reflection_spin.setToolTip(
            "Positive correction for façade or other sound reflections."
        )

        self.assessment_duration_spin = self._create_double_spinbox(
            minimum=0.01,
            maximum=48.0,
            value=8.0,
            decimals=2,
            suffix=" h",
        )

        self.activity_duration_spin = self._create_double_spinbox(
            minimum=0.01,
            maximum=48.0,
            value=4.0,
            decimals=2,
            suffix=" h",
        )

        input_form.addRow(
            "Source level:",
            self.source_level_spin,
        )
        input_form.addRow(
            "Source–receptor distance:",
            self.distance_spin,
        )
        input_form.addRow(
            "Ground condition:",
            self.ground_combo,
        )
        input_form.addRow(
            "Soft-ground proportion:",
            self.soft_ground_spin,
        )
        input_form.addRow(
            "Screening condition:",
            self.screening_combo,
        )
        input_form.addRow(
            "Reflection correction:",
            self.reflection_spin,
        )
        input_form.addRow(
            "Assessment period:",
            self.assessment_duration_spin,
        )
        input_form.addRow(
            "Activity operating time:",
            self.activity_duration_spin,
        )

        main_layout.addWidget(input_group)

        action_layout = QHBoxLayout()

        self.calculate_button = QPushButton("Calculate")
        self.calculate_button.setDefault(True)
        self.calculate_button.setMinimumHeight(36)

        self.reset_button = QPushButton("Reset")
        self.reset_button.setMinimumHeight(36)

        action_layout.addStretch()
        action_layout.addWidget(self.reset_button)
        action_layout.addWidget(self.calculate_button)

        main_layout.addLayout(action_layout)

        results_group = QGroupBox("Calculation results")
        results_layout = QGridLayout(results_group)

        self.distance_result_label = QLabel("—")
        self.ground_result_label = QLabel("—")
        self.screening_result_label = QLabel("—")
        self.reflection_result_label = QLabel("—")
        self.duration_result_label = QLabel("—")
        self.before_duration_result_label = QLabel("—")
        self.predicted_result_label = QLabel("—")

        result_labels = [
            self.distance_result_label,
            self.ground_result_label,
            self.screening_result_label,
            self.reflection_result_label,
            self.duration_result_label,
            self.before_duration_result_label,
        ]

        for label in result_labels:
            label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        results_layout.addWidget(
            QLabel("Distance attenuation:"),
            0,
            0,
        )
        results_layout.addWidget(
            self.distance_result_label,
            0,
            1,
        )

        results_layout.addWidget(
            QLabel("Ground attenuation:"),
            1,
            0,
        )
        results_layout.addWidget(
            self.ground_result_label,
            1,
            1,
        )

        results_layout.addWidget(
            QLabel("Screening attenuation:"),
            2,
            0,
        )
        results_layout.addWidget(
            self.screening_result_label,
            2,
            1,
        )

        results_layout.addWidget(
            QLabel("Reflection correction:"),
            3,
            0,
        )
        results_layout.addWidget(
            self.reflection_result_label,
            3,
            1,
        )

        results_layout.addWidget(
            QLabel("Duration correction:"),
            4,
            0,
        )
        results_layout.addWidget(
            self.duration_result_label,
            4,
            1,
        )

        results_layout.addWidget(
            QLabel("Level before duration:"),
            5,
            0,
        )
        results_layout.addWidget(
            self.before_duration_result_label,
            5,
            1,
        )

        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)

        results_layout.addWidget(separator, 6, 0, 1, 2)

        predicted_title = QLabel("Predicted noise level:")
        predicted_font = QFont()
        predicted_font.setBold(True)
        predicted_title.setFont(predicted_font)

        predicted_result_font = QFont()
        predicted_result_font.setPointSize(16)
        predicted_result_font.setBold(True)
        self.predicted_result_label.setFont(predicted_result_font)
        self.predicted_result_label.setAlignment(
            Qt.AlignRight | Qt.AlignVCenter
        )

        results_layout.addWidget(
            predicted_title,
            7,
            0,
        )
        results_layout.addWidget(
            self.predicted_result_label,
            7,
            1,
        )

        main_layout.addWidget(results_group)

        note_label = QLabel(
            "This is the first calculation-engine prototype. "
            "Map sources, receptor layers, DEM screening and spatial outputs "
            "will be connected in later phases."
        )
        note_label.setWordWrap(True)
        note_label.setStyleSheet(
            "QLabel { color: #666666; font-style: italic; }"
        )

        main_layout.addWidget(note_label)

        self.dialog_buttons = QDialogButtonBox(
            QDialogButtonBox.Close
        )
        main_layout.addWidget(self.dialog_buttons)

    def _connect_signals(self) -> None:
        """Connect button and widget events."""

        self.calculate_button.clicked.connect(
            self.calculate_prediction
        )
        self.reset_button.clicked.connect(
            self.reset_form
        )
        self.ground_combo.currentIndexChanged.connect(
            self._update_ground_controls
        )
        self.dialog_buttons.rejected.connect(
            self.reject
        )

    @staticmethod
    def _create_double_spinbox(
        minimum: float,
        maximum: float,
        value: float,
        decimals: int,
        suffix: str = "",
    ) -> QDoubleSpinBox:
        """Create a consistently configured numeric widget."""

        spinbox = QDoubleSpinBox()
        spinbox.setRange(minimum, maximum)
        spinbox.setValue(value)
        spinbox.setDecimals(decimals)
        spinbox.setSuffix(suffix)
        spinbox.setSingleStep(1.0)
        spinbox.setKeyboardTracking(False)

        return spinbox

    def _selected_ground_type(self) -> GroundType:
        """Return the selected ground type."""

        return self.ground_combo.currentData()

    def _selected_screening_type(self) -> ScreeningType:
        """Return the selected screening type."""

        return self.screening_combo.currentData()

    def _update_ground_controls(self) -> None:
        """Enable soft-ground percentage only for mixed ground."""

        is_mixed = (
            self._selected_ground_type()
            == GroundType.MIXED
        )

        self.soft_ground_spin.setEnabled(is_mixed)

        if not is_mixed:
            self.soft_ground_spin.setToolTip(
                "Only used when Mixed ground is selected."
            )
        else:
            self.soft_ground_spin.setToolTip(
                "Percentage of the propagation path treated as soft ground."
            )

    def _validate_inputs(self) -> bool:
        """Validate relationships between GUI inputs."""

        activity_duration = self.activity_duration_spin.value()
        assessment_duration = self.assessment_duration_spin.value()

        if activity_duration > assessment_duration:
            QMessageBox.warning(
                self,
                "Invalid duration",
                "Activity operating time cannot exceed "
                "the assessment period.",
            )
            self.activity_duration_spin.setFocus()
            return False

        return True

    def calculate_prediction(self) -> None:
        """Read inputs, run the engine and display results."""

        if not self._validate_inputs():
            return

        try:
            prediction_input = PredictionInput(
                source_level_db=self.source_level_spin.value(),
                distance_m=self.distance_spin.value(),
                ground_type=self._selected_ground_type(),
                soft_ground_percent=self.soft_ground_spin.value(),
                screening_type=self._selected_screening_type(),
                reflection_correction_db=self.reflection_spin.value(),
                activity_duration_hours=(
                    self.activity_duration_spin.value()
                ),
                assessment_duration_hours=(
                    self.assessment_duration_spin.value()
                ),
            )

            result = predict_noise_level(prediction_input)
            result = round_result(result, decimals=1)

            self.distance_result_label.setText(
                f"−{result.distance_attenuation_db:.1f} dB"
            )
            self.ground_result_label.setText(
                f"−{result.ground_attenuation_db:.1f} dB"
            )
            self.screening_result_label.setText(
                f"−{result.screening_attenuation_db:.1f} dB"
            )
            self.reflection_result_label.setText(
                f"+{result.reflection_correction_db:.1f} dB"
            )
            self.duration_result_label.setText(
                f"{result.duration_correction_db:+.1f} dB"
            )
            self.before_duration_result_label.setText(
                f"{result.level_before_duration_db:.1f} dB"
            )
            self.predicted_result_label.setText(
                f"{result.predicted_level_db:.1f} dB"
            )

        except ValueError as error:
            QMessageBox.warning(
                self,
                "Calculation error",
                str(error),
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "Unexpected error",
                (
                    "The prediction could not be completed.\n\n"
                    f"Details: {error}"
                ),
            )

    def _clear_results(self) -> None:
        """Clear all calculated values."""

        self.distance_result_label.setText("—")
        self.ground_result_label.setText("—")
        self.screening_result_label.setText("—")
        self.reflection_result_label.setText("—")
        self.duration_result_label.setText("—")
        self.before_duration_result_label.setText("—")
        self.predicted_result_label.setText("—")

    def reset_form(self) -> None:
        """Restore default values."""

        self.source_level_spin.setValue(90.0)
        self.distance_spin.setValue(100.0)

        self.ground_combo.setCurrentIndex(0)
        self.soft_ground_spin.setValue(50.0)

        self.screening_combo.setCurrentIndex(0)
        self.reflection_spin.setValue(0.0)

        self.assessment_duration_spin.setValue(8.0)
        self.activity_duration_spin.setValue(4.0)

        self._update_ground_controls()
        self._clear_results()