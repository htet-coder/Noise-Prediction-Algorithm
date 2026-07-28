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
    QAbstractItemView,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from qgis.core import (
    Qgis,
    QgsCoordinateTransform,
    QgsDistanceArea,
    QgsFeature,
    QgsMapLayerProxyModel,
    QgsProject,
    QgsVectorLayer,
    QgsWkbTypes,
)
from qgis.gui import QgsMapLayerComboBox

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
        self.resize(900,700)

        self.setMinimumSize(800,600)

        self._connected_source_layer = None

        self._build_ui()
        self._connect_signals()
        self._update_ground_controls()
        self._update_layer_status()
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
        
        layer_group = QGroupBox(
            "QGIS source and receptor layers"
        )
        layer_form = QFormLayout(layer_group)

        self.source_layer_combo = QgsMapLayerComboBox()
        self.source_layer_combo.setFilters(
            QgsMapLayerProxyModel.Filter.PointLayer
        )
        self.source_layer_combo.setAllowEmptyLayer(True)

        self.receptor_layer_combo = QgsMapLayerComboBox()
        self.receptor_layer_combo.setFilters(
            QgsMapLayerProxyModel.Filter.PointLayer
        )
        self.receptor_layer_combo.setAllowEmptyLayer(True)

        self.source_status_label = QLabel(
            "Select exactly one source feature on the map."
        )
        self.source_status_label.setWordWrap(True)

        self.receptor_status_label = QLabel(
            "All receptor features will be calculated."
        )
        self.receptor_status_label.setWordWrap(True)

        layer_form.addRow(
            "Source point layer:",
            self.source_layer_combo,
        )
        layer_form.addRow(
            "Source selection:",
            self.source_status_label,
        )
        layer_form.addRow(
            "Receptor point layer:",
            self.receptor_layer_combo,
        )
        layer_form.addRow(
            "Receptors:",
            self.receptor_status_label,
        )

        main_layout.addWidget(layer_group)        
        
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

        self.distance_spin.setEnabled(False)
        self.distance_spin.setToolTip(
            "Distance is calculated automatically from the selected "
            "source and receptor geometries."
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
            "Preview distance:",
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

        self.calculate_button = QPushButton(
            "Calculate selected source"
        )
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
        table_group = QGroupBox("Receptor prediction results")
        table_layout = QVBoxLayout(table_group)

        self.results_table = QTableWidget()
        self.results_table.setColumnCount(8)

        self.results_table.setHorizontalHeaderLabels(
            [
                "Receptor ID",
                "Distance (m)",
                "Distance Att. (dB)",
                "Ground Att. (dB)",
                "Screening (dB)",
                "Reflection (dB)",
                "Duration (dB)",
                "Predicted Level (dB)",
            ]
        )

        self.results_table.setEditTriggers(
            QAbstractItemView.NoEditTriggers
        )
        self.results_table.setSelectionBehavior(
            QAbstractItemView.SelectRows
        )
        self.results_table.setAlternatingRowColors(True)
        self.results_table.verticalHeader().setVisible(False)

        header = self.results_table.horizontalHeader()
        header.setSectionResizeMode(
            QHeaderView.ResizeToContents
        )
        header.setStretchLastSection(True)

        table_layout.addWidget(self.results_table)

        main_layout.addWidget(table_group)

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

        self.source_layer_combo.layerChanged.connect(
            self._on_source_layer_changed
        )

        self.receptor_layer_combo.layerChanged.connect(
            self._update_layer_status
        )

        self.dialog_buttons.rejected.connect(
            self.reject
        )

    def _on_source_layer_changed(self, layer) -> None:
        """Reconnect source selection monitoring when the layer changes."""

        if self._connected_source_layer is not None:
            try:
                self._connected_source_layer.selectionChanged.disconnect(
                    self._update_layer_status
                )
            except (TypeError, RuntimeError):
                pass

        self._connected_source_layer = layer

        if layer is not None:
            try:
                layer.selectionChanged.connect(
                    self._update_layer_status
                )
            except (AttributeError, TypeError):
                pass

        self._update_layer_status()

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

    def _update_layer_status(self, *args) -> None:
        """Show source selection and receptor feature information."""

        source_layer = self.source_layer_combo.currentLayer()
        receptor_layer = self.receptor_layer_combo.currentLayer()

        if source_layer is None:
            self.source_status_label.setText(
                "No source layer selected."
            )
        else:
            selected_count = source_layer.selectedFeatureCount()

            if selected_count == 0:
                self.source_status_label.setText(
                    "No source selected. Use the QGIS Select Features "
                    "tool and select one source point."
                )

            elif selected_count == 1:
                selected_feature = next(
                    source_layer.getSelectedFeatures()
                )

                self.source_status_label.setText(
                    f"Source feature selected: {selected_feature.id()}"
                )

            else:
                self.source_status_label.setText(
                    f"{selected_count} source features selected. "
                    "Please keep only one selected."
                )

        if receptor_layer is None:
            self.receptor_status_label.setText(
                "No receptor layer selected."
            )
        else:
            count = receptor_layer.featureCount()

            self.receptor_status_label.setText(
                f"{count} receptor feature(s) available."
            )

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
        """Calculate noise predictions for all receptor features."""

        if not self._validate_inputs():
            return

        source_layer = self.source_layer_combo.currentLayer()
        receptor_layer = self.receptor_layer_combo.currentLayer()

        if source_layer is None:
            QMessageBox.warning(
                self,
                "Source layer required",
                "Select a source point layer.",
            )
            return

        if receptor_layer is None:
            QMessageBox.warning(
                self,
                "Receptor layer required",
                "Select a receptor point layer.",
            )
            return

        if source_layer.selectedFeatureCount() != 1:
            QMessageBox.warning(
                self,
                "Select one source",
                "Use the QGIS Select Features tool and select "
                "exactly one source point.",
            )
            return

        receptor_count = receptor_layer.featureCount()

        if receptor_count == 0:
            QMessageBox.warning(
                self,
                "No receptors",
                "The selected receptor layer has no features.",
            )
            return

        try:
            source_feature = next(
                source_layer.getSelectedFeatures()
            )

            source_point = self._point_from_feature(
                source_feature
            )

            self.results_table.setRowCount(0)

            first_result = None
            successful_count = 0
            error_messages = []

            for receptor_feature in receptor_layer.getFeatures():
                try:
                    receptor_point = self._point_from_feature(
                        receptor_feature
                    )

                    distance_m = self._measure_distance_metres(
                        source_point=source_point,
                        receptor_point=receptor_point,
                        source_layer=source_layer,
                        receptor_layer=receptor_layer,
                    )

                    prediction_input = PredictionInput(
                        source_level_db=(
                            self.source_level_spin.value()
                        ),
                        distance_m=distance_m,
                        ground_type=(
                            self._selected_ground_type()
                        ),
                        soft_ground_percent=(
                            self.soft_ground_spin.value()
                        ),
                        screening_type=(
                            self._selected_screening_type()
                        ),
                        reflection_correction_db=(
                            self.reflection_spin.value()
                        ),
                        activity_duration_hours=(
                            self.activity_duration_spin.value()
                        ),
                        assessment_duration_hours=(
                            self.assessment_duration_spin.value()
                        ),
                    )

                    result = predict_noise_level(
                        prediction_input
                    )
                    result = round_result(
                        result,
                        decimals=1,
                    )

                    if first_result is None:
                        first_result = result

                    self._add_result_row(
                        receptor_feature=receptor_feature,
                        result=result,
                    )

                    successful_count += 1

                except Exception as receptor_error:
                    error_messages.append(
                        f"Receptor {receptor_feature.id()}: "
                        f"{receptor_error}"
                    )

            if first_result is not None:
                self._show_summary_result(first_result)

                self.distance_spin.setValue(
                    first_result.distance_m
                )

            if successful_count == 0:
                raise ValueError(
                    "No receptor predictions were completed."
                )

            message = (
                f"Completed predictions for "
                f"{successful_count} receptor(s)."
            )

            if error_messages:
                message += (
                    f"\n\n{len(error_messages)} receptor(s) "
                    "could not be calculated."
                )

            QMessageBox.information(
                self,
                "Prediction complete",
                message,
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
                    "The spatial prediction could not be completed."
                    f"\n\nDetails: {error}"
                ),
            )

    def _add_result_row(
        self,
        receptor_feature: QgsFeature,
        result,
    ) -> None:
        """Add one receptor prediction to the table."""

        row = self.results_table.rowCount()
        self.results_table.insertRow(row)

        receptor_id = self._receptor_identifier(
            receptor_feature
        )

        values = [
            receptor_id,
            f"{result.distance_m:.1f}",
            f"{result.distance_attenuation_db:.1f}",
            f"{result.ground_attenuation_db:.1f}",
            f"{result.screening_attenuation_db:.1f}",
            f"{result.reflection_correction_db:.1f}",
            f"{result.duration_correction_db:.1f}",
            f"{result.predicted_level_db:.1f}",
        ]

        for column, value in enumerate(values):
            item = QTableWidgetItem(value)

            if column > 0:
                item.setTextAlignment(
                    Qt.AlignRight | Qt.AlignVCenter
                )

            item.setData(
                Qt.UserRole,
                receptor_feature.id(),
            )

            self.results_table.setItem(
                row,
                column,
                item,
            )


    def _show_summary_result(self, result) -> None:
        """Show the first receptor result in the summary panel."""

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

        def _on_source_layer_changed(self, layer) -> None:
            """Reconnect source selection monitoring when layer changes."""

            try:
                layer.selectionChanged.connect(
                    self._update_layer_status
                )
            except (AttributeError, TypeError):
                pass

            self._update_layer_status()


    @staticmethod
    def _point_from_feature(feature: QgsFeature):
        """Return a point from a point or multipoint feature."""

        geometry = feature.geometry()

        if geometry is None or geometry.isEmpty():
            raise ValueError(
                f"Feature {feature.id()} has empty geometry."
            )

        geometry_type = QgsWkbTypes.geometryType(
            geometry.wkbType()
        )

        if geometry_type != Qgis.GeometryType.Point:
            raise ValueError(
                f"Feature {feature.id()} is not a point feature."
            )

        if geometry.isMultipart():
            points = geometry.asMultiPoint()

            if not points:
                raise ValueError(
                    f"Feature {feature.id()} has no valid point."
                )

            return points[0]

        return geometry.asPoint()


    def _create_distance_calculator(
        self,
        layer: QgsVectorLayer,
    ) -> QgsDistanceArea:
        """Create a CRS-aware QGIS distance calculator."""

        distance_area = QgsDistanceArea()

        project = QgsProject.instance()

        distance_area.setSourceCrs(
            layer.crs(),
            project.transformContext(),
        )

        ellipsoid = project.ellipsoid()

        if ellipsoid:
            distance_area.setEllipsoid(ellipsoid)

        return distance_area

    @staticmethod
    def _receptor_identifier(feature: QgsFeature) -> str:
        """Return a readable receptor identifier."""

        candidate_fields = (
            "receptor_id",
            "site_id",
            "name",
            "id",
            "ID",
        )

        field_names = feature.fields().names()

        for field_name in candidate_fields:
            if field_name in field_names:
                value = feature[field_name]

                if value not in (None, ""):
                    return str(value)

        return str(feature.id())
        
    def _measure_distance_metres(
        self,
        source_point,
        receptor_point,
        source_layer: QgsVectorLayer,
        receptor_layer: QgsVectorLayer,
    ) -> float:
        """Measure source-to-receptor distance in metres."""

        project = QgsProject.instance()
        transformed_receptor = receptor_point

        if source_layer.crs() != receptor_layer.crs():
            coordinate_transform = QgsCoordinateTransform(
                receptor_layer.crs(),
                source_layer.crs(),
                project.transformContext(),
            )

            transformed_receptor = coordinate_transform.transform(
                receptor_point
            )

        distance_area = QgsDistanceArea()
        distance_area.setSourceCrs(
            source_layer.crs(),
            project.transformContext(),
        )

        ellipsoid = project.ellipsoid()

        if ellipsoid:
            distance_area.setEllipsoid(ellipsoid)

        distance_m = distance_area.measureLine(
            source_point,
            transformed_receptor,
        )

        if distance_m <= 0:
            raise ValueError(
                "Source and receptor cannot occupy the same location."
            )

        return distance_m
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
        self.results_table.setRowCount(0)
        self._update_layer_status()
    def _clear_results(self) -> None:
        """Clear all calculated values."""

        self.distance_result_label.setText("—")
        self.ground_result_label.setText("—")
        self.screening_result_label.setText("—")
        self.reflection_result_label.setText("—")
        self.duration_result_label.setText("—")
        self.before_duration_result_label.setText("—")
        self.predicted_result_label.setText("—")

        self.results_table.setRowCount(0)