# -*- coding: utf-8 -*-
from __future__ import annotations

import csv
import os
import re

from qgis.PyQt import uic
from qgis.PyQt.QtCore import Qt, QVariant
from qgis.PyQt.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QFileDialog,
    QHeaderView,
    QMessageBox,
    QTableWidgetItem,
)
from qgis.core import (
    Qgis,
    QgsCoordinateTransform,
    QgsDistanceArea,
    QgsFeature,
    QgsFeatureRequest,
    QgsFieldProxyModel,
    QgsField,
    QgsGraduatedSymbolRenderer,
    QgsMarkerSymbol,
    QgsMapLayerProxyModel,
    QgsProject,
    QgsRendererRange,
    QgsVectorFileWriter,
    QgsVectorLayer,
    QgsWkbTypes,
)
from qgis.utils import iface

from ..core.bs5228_engine import (
    GroundType,
    PredictionInput,
    ScreeningType,
    predict_noise_level,
    round_result,
    logarithmic_sum,
)

from ..models.source_model import SourceModel
from ..validation.source_validator import SourceValidator

FORM_CLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "noise_prediction_dialog.ui")
)


class NoisePredictionDialog(QDialog, FORM_CLASS):
    """Qt Designer based BS 5228 prediction dialog."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self._connected_source_layer = None
        self._current_output_layer = None
        self._current_receptor_layer = None
        self._source_validator = SourceValidator()
        self._configure_widgets()
        self._populate_choices()
        self._connect_signals()
        self._update_ground_controls()
        self._update_calculation_mode()
        self._update_source_level_controls()
        self._update_source_specific_controls()
        self._update_output_controls()
        self._update_layer_status()
        self._clear_results()

    def _configure_widgets(self) -> None:
        self.sourceLayerCombo.setFilters(QgsMapLayerProxyModel.Filter.PointLayer)
        self.sourceLayerCombo.setAllowEmptyLayer(True)
        self.receptorLayerCombo.setFilters(QgsMapLayerProxyModel.Filter.PointLayer)
        self.receptorLayerCombo.setAllowEmptyLayer(True)

        self.sourceLevelFieldCombo.setFilters(QgsFieldProxyModel.AllTypes)
        self.sourceLevelFieldCombo.setLayer(self.sourceLayerCombo.currentLayer())

        # Phase 4C source-specific activity attribute fields.
        self.activityFieldCombo.setFilters(QgsFieldProxyModel.AllTypes)
        self.equipmentFieldCombo.setFilters(QgsFieldProxyModel.AllTypes)
        # Allow numeric database fields and text fields containing numeric values.
        # Values are converted and validated when SourceModel objects are built.
        self.durationFieldCombo.setFilters(QgsFieldProxyModel.AllTypes)
        self.groundFieldCombo.setFilters(QgsFieldProxyModel.AllTypes)
        self.screeningFieldCombo.setFilters(QgsFieldProxyModel.AllTypes)
        self.reflectionFieldCombo.setFilters(QgsFieldProxyModel.AllTypes)

        source_layer = self.sourceLayerCombo.currentLayer()
        for combo in self._activity_field_combos():
            combo.setAllowEmptyFieldName(True)
            combo.setLayer(source_layer)

        self.resultsTable.setColumnCount(7)
        self.resultsTable.setHorizontalHeaderLabels([
            "Receptor ID", "Source Count", "Nearest Distance (m)",
            "Dominant Source", "Dominant Source Level (dB)",
            "Highest Contribution (dB)", "Combined Level (dB)",
        ])
        self.resultsTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.resultsTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.resultsTable.setAlternatingRowColors(True)
        self.resultsTable.verticalHeader().setVisible(False)
        header = self.resultsTable.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setStretchLastSection(True)
        self.resultsTable.setSelectionMode(QAbstractItemView.SingleSelection)
        self._set_results_actions_enabled(False)

    def _activity_field_combos(self):
        """Return all Phase 4C source-attribute field selectors."""

        return (
            self.activityFieldCombo,
            self.equipmentFieldCombo,
            self.durationFieldCombo,
            self.groundFieldCombo,
            self.screeningFieldCombo,
            self.reflectionFieldCombo,
        )

    def _populate_choices(self) -> None:
        self.sourceLevelModeCombo.clear()
        self.sourceLevelModeCombo.addItem("Use one level for all selected sources", "common")
        self.sourceLevelModeCombo.addItem("Read level from source attribute field", "field")

        self.groundCombo.clear()
        self.groundCombo.addItem("Hard ground", GroundType.HARD)
        self.groundCombo.addItem("Soft ground", GroundType.SOFT)
        self.groundCombo.addItem("Mixed ground", GroundType.MIXED)

        self.screeningCombo.clear()
        self.screeningCombo.addItem("No screening — 0 dB", ScreeningType.NONE)
        self.screeningCombo.addItem("Partial screening — 5 dB", ScreeningType.PARTIAL)
        self.screeningCombo.addItem("Full screening — 10 dB", ScreeningType.FULL)

    def _connect_signals(self) -> None:
        self.calculateButton.clicked.connect(self.calculate_prediction)
        self.resetButton.clicked.connect(self.reset_form)
        self.nextButton.clicked.connect(self._go_to_output_tab)
        self.backButton.clicked.connect(self._go_to_inputs_tab)
        self.simpleModeRadio.toggled.connect(self._update_calculation_mode)
        self.sourceSpecificModeRadio.toggled.connect(
            self._update_calculation_mode
        )
        self.groundCombo.currentIndexChanged.connect(self._update_ground_controls)
        self.sourceLevelModeCombo.currentIndexChanged.connect(self._update_source_level_controls)
        self.sourceLayerCombo.layerChanged.connect(self._on_source_layer_changed)
        self.receptorLayerCombo.layerChanged.connect(self._update_layer_status)
        self.temporaryOutputRadio.toggled.connect(self._update_output_controls)
        self.permanentOutputRadio.toggled.connect(self._update_output_controls)
        self.shapefileOutputRadio.toggled.connect(self._update_output_controls)
        self.browseOutputButton.clicked.connect(self._browse_output_file)

        for combo in self._activity_field_combos():
            combo.fieldChanged.connect(self._update_source_specific_controls)
        self.resultsTable.itemSelectionChanged.connect(
            self._on_result_selection_changed
        )
        self.resultsTable.cellDoubleClicked.connect(
            self._zoom_to_selected_receptor
        )
        self.selectReceptorButton.clicked.connect(
            self._select_receptor_from_table
        )
        self.zoomReceptorButton.clicked.connect(
            self._zoom_to_selected_receptor
        )
        self.exportCsvButton.clicked.connect(self._export_results_csv)
        self.dialogButtons.rejected.connect(self.reject)

    def _on_source_layer_changed(self, layer) -> None:
        if self._connected_source_layer is not None:
            try:
                self._connected_source_layer.selectionChanged.disconnect(
                    self._update_layer_status
                )
            except (TypeError, RuntimeError):
                pass

        self._connected_source_layer = layer
        self.sourceLevelFieldCombo.setLayer(layer)
        for combo in self._activity_field_combos():
            combo.setLayer(layer)

        if layer is not None:
            try:
                layer.selectionChanged.connect(self._update_layer_status)
            except (AttributeError, TypeError):
                pass
        self._update_source_specific_controls()
        self._update_layer_status()

    def _is_source_specific_mode(self) -> bool:
        """Return True when the Phase 4C source-specific workflow is active."""

        return self.sourceSpecificModeRadio.isChecked()

    def _update_calculation_mode(self, *args) -> None:
        """Apply a clear Simple versus Source-Specific workflow."""

        specific_mode = self._is_source_specific_mode()
        self.activityAttributesGroupBox.setEnabled(specific_mode)

        if specific_mode:
            # Source-Specific mode always reads an individual sound level.
            field_index = self.sourceLevelModeCombo.findData("field")
            if field_index >= 0:
                self.sourceLevelModeCombo.setCurrentIndex(field_index)
            self.sourceLevelModeCombo.setEnabled(False)
            self.sourceLevelModeLabel.setEnabled(False)
            self.sourceLevelHelpLabel.setText(
                "Source-Specific mode requires a source-level field. "
                "Numeric fields and text fields containing numeric values are supported. "
                "Mapped duration, ground, screening and reflection fields override "
                "the fallback values below."
            )
        else:
            self.sourceLevelModeCombo.setEnabled(True)
            self.sourceLevelModeLabel.setEnabled(True)
            self.sourceLevelHelpLabel.setText(
                "Choose one common source level or read only the sound level "
                "from a source attribute field. Other source-specific mappings "
                "are disabled in Simple mode."
            )

        self._update_source_level_controls()
        self._update_source_specific_controls()

    def _go_to_output_tab(self) -> None:
        """Validate the input-stage configuration and open Output options."""

        if not self._validate_input_stage():
            return
        self.tabWidget.setCurrentWidget(self.outputTab)

    def _go_to_inputs_tab(self) -> None:
        """Return to Inputs without clearing the current configuration."""

        self.tabWidget.setCurrentWidget(self.inputsTab)

    def _validate_input_stage(self) -> bool:
        """Validate layers and calculation settings before Output options."""

        source_layer = self.sourceLayerCombo.currentLayer()
        receptor_layer = self.receptorLayerCombo.currentLayer()

        if source_layer is None or receptor_layer is None:
            QMessageBox.warning(
                self,
                "Layers required",
                "Select both a source point layer and a receptor point layer.",
            )
            return False

        if source_layer.selectedFeatureCount() == 0:
            QMessageBox.warning(
                self,
                "Select sources",
                "Select one or more source points with the QGIS selection tool.",
            )
            return False

        if receptor_layer.featureCount() == 0:
            QMessageBox.warning(
                self,
                "No receptors",
                "The receptor layer is empty.",
            )
            return False

        if (
            not self.durationFieldCombo.currentField()
            and self.activityDurationSpin.value()
            > self.assessmentDurationSpin.value()
        ):
            QMessageBox.warning(
                self,
                "Invalid duration",
                "Activity operating time cannot exceed the assessment period.",
            )
            self.activityDurationSpin.setFocus()
            return False

        if self._uses_source_level_field() and not (
            self.sourceLevelFieldCombo.currentField()
        ):
            QMessageBox.warning(
                self,
                "Source-level field required",
                "Select the source attribute containing the sound level in dB. "
                "Numeric fields and text fields containing numeric values are supported.",
            )
            self.sourceLevelFieldCombo.setFocus()
            return False

        return True

    def _uses_source_level_field(self) -> bool:
        return self.sourceLevelModeCombo.currentData() == "field"

    def _update_source_level_controls(self, *args) -> None:
        use_field = self._uses_source_level_field()
        self.sourceLevelFieldLabel.setEnabled(use_field)
        self.sourceLevelFieldCombo.setEnabled(use_field)
        self.sourceLevelSpin.setEnabled(not use_field)
        self.sourceLevelLabel.setEnabled(not use_field)

    def _source_level_for_feature(self, feature: QgsFeature) -> float:
        if not self._uses_source_level_field():
            return float(self.sourceLevelSpin.value())

        field_name = self.sourceLevelFieldCombo.currentField()
        if not field_name:
            raise ValueError("Select a numeric source-level attribute field.")

        value = feature[field_name]

        if value is None or str(value).strip() == "":
            raise ValueError(
                f"Source {self._source_identifier(feature)} has an empty value "
                f"in sound-level field '{field_name}'."
            )

        try:
            level = float(str(value).strip())
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"Source {self._source_identifier(feature)} has an invalid "
                f"sound-level value in field '{field_name}': {value!r}. "
                "Enter a numeric value in dB, for example 90 or 90.5."
            ) from exc
        if not 0.0 <= level <= 200.0:
            raise ValueError(
                f"Source {self._source_identifier(feature)} has level {level} dB; "
                "source levels must be between 0 and 200 dB."
            )
        return level

    @staticmethod
    def _optional_field_value(feature: QgsFeature, field_combo):
        """Read an optional attribute selected in a QgsFieldComboBox."""

        field_name = field_combo.currentField()
        if not field_name:
            return None

        value = feature[field_name]
        if value is None:
            return None

        return value

    def _optional_text_value(
        self,
        feature: QgsFeature,
        field_combo,
        default: str = "",
    ) -> str:
        """Read optional text from a source feature."""

        value = self._optional_field_value(feature, field_combo)
        if value is None:
            return default

        text = str(value).strip()
        return text if text else default

    def _optional_numeric_value(
        self,
        feature: QgsFeature,
        field_combo,
        default: float,
        label: str,
    ) -> float:
        """Read an optional numeric attribute, using a global fallback."""

        value = self._optional_field_value(feature, field_combo)
        if value is None or value == "":
            return float(default)

        try:
            return float(value)
        except (TypeError, ValueError) as exc:
            source_id = self._source_identifier(feature)
            field_name = field_combo.currentField()
            raise ValueError(
                f"Source {source_id} has an invalid {label} value "
                f"in field '{field_name}': {value}"
            ) from exc

    @staticmethod
    def _normalise_ground_type(value) -> GroundType:
        """Convert a source attribute value into a GroundType."""

        if isinstance(value, GroundType):
            return value

        text = str(value).strip().lower()
        aliases = {
            "hard": GroundType.HARD,
            "hard ground": GroundType.HARD,
            "0": GroundType.HARD,
            "soft": GroundType.SOFT,
            "soft ground": GroundType.SOFT,
            "1": GroundType.SOFT,
            "mixed": GroundType.MIXED,
            "mixed ground": GroundType.MIXED,
            "2": GroundType.MIXED,
        }

        if text in aliases:
            return aliases[text]

        raise ValueError(
            f"Unsupported ground value '{value}'. "
            "Use Hard, Soft, or Mixed."
        )

    @staticmethod
    def _normalise_screening_type(value) -> ScreeningType:
        """Convert a source attribute value into a ScreeningType."""

        if isinstance(value, ScreeningType):
            return value

        text = str(value).strip().lower()
        aliases = {
            "none": ScreeningType.NONE,
            "no": ScreeningType.NONE,
            "no screening": ScreeningType.NONE,
            "0": ScreeningType.NONE,
            "partial": ScreeningType.PARTIAL,
            "partial screening": ScreeningType.PARTIAL,
            "5": ScreeningType.PARTIAL,
            "full": ScreeningType.FULL,
            "full screening": ScreeningType.FULL,
            "10": ScreeningType.FULL,
        }

        if text in aliases:
            return aliases[text]

        raise ValueError(
            f"Unsupported screening value '{value}'. "
            "Use None, Partial, or Full."
        )

    def _source_model_from_feature(self, feature: QgsFeature) -> SourceModel:
        """Convert one selected source feature into the shared source model."""

        if not self._is_source_specific_mode():
            return SourceModel(
                feature_id=int(feature.id()),
                source_id=self._source_identifier(feature),
                activity="",
                equipment="",
                level_db=self._source_level_for_feature(feature),
                duration_hours=float(self.activityDurationSpin.value()),
                ground_type=self._selected_ground_type(),
                screening=self._selected_screening_type(),
                reflection_db=float(self.reflectionSpin.value()),
                geometry=self._point_from_feature(feature),
            )

        ground_value = self._optional_field_value(
            feature,
            self.groundFieldCombo,
        )
        if ground_value is None or ground_value == "":
            ground_type = self._selected_ground_type()
        else:
            ground_type = self._normalise_ground_type(ground_value)

        screening_value = self._optional_field_value(
            feature,
            self.screeningFieldCombo,
        )
        if screening_value is None or screening_value == "":
            screening_type = self._selected_screening_type()
        else:
            screening_type = self._normalise_screening_type(screening_value)

        duration_hours = self._optional_numeric_value(
            feature,
            self.durationFieldCombo,
            self.activityDurationSpin.value(),
            "activity duration",
        )
        assessment_hours = float(self.assessmentDurationSpin.value())
        if duration_hours <= 0:
            raise ValueError(
                f"Source {self._source_identifier(feature)} has an activity "
                "duration that must be greater than zero."
            )
        if duration_hours > assessment_hours:
            raise ValueError(
                f"Source {self._source_identifier(feature)} has activity duration "
                f"{duration_hours:g} h, exceeding the assessment period "
                f"{assessment_hours:g} h."
            )

        return SourceModel(
            feature_id=int(feature.id()),
            source_id=self._source_identifier(feature),
            activity=self._optional_text_value(
                feature,
                self.activityFieldCombo,
            ),
            equipment=self._optional_text_value(
                feature,
                self.equipmentFieldCombo,
            ),
            level_db=self._source_level_for_feature(feature),
            duration_hours=duration_hours,
            ground_type=ground_type,
            screening=screening_type,
            reflection_db=self._optional_numeric_value(
                feature,
                self.reflectionFieldCombo,
                self.reflectionSpin.value(),
                "reflection correction",
            ),
            geometry=self._point_from_feature(feature),
        )

    def _selected_ground_type(self) -> GroundType:
        return self.groundCombo.currentData()

    def _selected_screening_type(self) -> ScreeningType:
        return self.screeningCombo.currentData()

    def _update_ground_controls(self, *args) -> None:
        # A mapped ground field may contain Mixed values, so the global soft-ground
        # proportion remains available as the shared mixed-ground proportion.
        ground_is_mapped = bool(self.groundFieldCombo.currentField())
        self.softGroundSpin.setEnabled(
            ground_is_mapped or self._selected_ground_type() == GroundType.MIXED
        )

    def _update_source_specific_controls(self, *args) -> None:
        """Enable mapped overrides only in Source-Specific mode."""

        specific_mode = self._is_source_specific_mode()
        duration_mapped = (
            specific_mode and bool(self.durationFieldCombo.currentField())
        )
        ground_mapped = (
            specific_mode and bool(self.groundFieldCombo.currentField())
        )
        screening_mapped = (
            specific_mode and bool(self.screeningFieldCombo.currentField())
        )
        reflection_mapped = (
            specific_mode and bool(self.reflectionFieldCombo.currentField())
        )

        self.activityDurationSpin.setEnabled(not duration_mapped)
        self.activityLabel.setEnabled(not duration_mapped)
        self.groundCombo.setEnabled(not ground_mapped)
        self.groundLabel.setEnabled(not ground_mapped)
        self.screeningCombo.setEnabled(not screening_mapped)
        self.screeningLabel.setEnabled(not screening_mapped)
        self.reflectionSpin.setEnabled(not reflection_mapped)
        self.reflectionLabel.setEnabled(not reflection_mapped)
        self._update_ground_controls()

    def _update_output_controls(self, *args) -> None:
        permanent = (
            self.permanentOutputRadio.isChecked()
            or self.shapefileOutputRadio.isChecked()
        )
        self.outputPathEdit.setEnabled(permanent)
        self.browseOutputButton.setEnabled(permanent)

        if self.permanentOutputRadio.isChecked():
            self.outputPathLabel.setText("GeoPackage file:")
            self.outputPathEdit.setPlaceholderText("Select or create a .gpkg file")
        elif self.shapefileOutputRadio.isChecked():
            self.outputPathLabel.setText("Shapefile:")
            self.outputPathEdit.setPlaceholderText("Select or create a .shp file")
        else:
            self.outputPathLabel.setText("Output file:")
            self.outputPathEdit.setPlaceholderText(
                "Select GeoPackage or Shapefile output"
            )

    def _browse_output_file(self) -> None:
        start_path = self.outputPathEdit.text().strip()
        if not start_path:
            project_path = QgsProject.instance().homePath()
            start_path = project_path or os.path.expanduser("~")

        if self.shapefileOutputRadio.isChecked():
            caption = "Save prediction output as Shapefile"
            file_filter = "ESRI Shapefile (*.shp)"
            extension = ".shp"
        else:
            caption = "Save prediction output as GeoPackage"
            file_filter = "GeoPackage (*.gpkg)"
            extension = ".gpkg"

        path, _ = QFileDialog.getSaveFileName(
            self,
            caption,
            start_path,
            file_filter,
        )
        if path:
            if not path.lower().endswith(extension):
                path += extension
            self.outputPathEdit.setText(path)

    def _update_layer_status(self, *args) -> None:
        source_layer = self.sourceLayerCombo.currentLayer()
        receptor_layer = self.receptorLayerCombo.currentLayer()

        if source_layer is None:
            self.sourceStatusLabel.setText("No source layer selected.")
        else:
            count = source_layer.selectedFeatureCount()
            if count == 0:
                self.sourceStatusLabel.setText(
                    "No sources selected. Select one or more source points in QGIS."
                )
            elif count == 1:
                feature = next(source_layer.getSelectedFeatures())
                self.sourceStatusLabel.setText(
                    f"1 source selected: {self._source_identifier(feature)}"
                )
            else:
                self.sourceStatusLabel.setText(
                    f"{count} source features selected for cumulative prediction."
                )

        if receptor_layer is None:
            self.receptorStatusLabel.setText("No receptor layer selected.")
        else:
            self.receptorStatusLabel.setText(
                f"{receptor_layer.featureCount()} receptor feature(s) available."
            )

    def _validate_inputs(self) -> bool:
        if not self._validate_input_stage():
            self.tabWidget.setCurrentWidget(self.inputsTab)
            return False

        if not self.outputLayerNameEdit.text().strip():
            QMessageBox.warning(
                self,
                "Output name required",
                "Enter an output layer name.",
            )
            self.outputLayerNameEdit.setFocus()
            return False

        permanent = (
            self.permanentOutputRadio.isChecked()
            or self.shapefileOutputRadio.isChecked()
        )
        if permanent:
            output_path = self.outputPathEdit.text().strip()
            if not output_path:
                QMessageBox.warning(
                    self,
                    "Output file required",
                    "Select an output file for the permanent layer.",
                )
                self.outputPathEdit.setFocus()
                return False

            required_extension = (
                ".shp" if self.shapefileOutputRadio.isChecked() else ".gpkg"
            )
            if not output_path.lower().endswith(required_extension):
                QMessageBox.warning(
                    self,
                    "Invalid output file",
                    f"The selected output type requires the "
                    f"{required_extension} extension.",
                )
                self.outputPathEdit.setFocus()
                return False

        return True

    def _validate_source_models(self, source_models) -> bool:
        """Validate all source models before starting receptor calculations."""

        report = self._source_validator.validate(
            source_models,
            source_specific_mode=self._is_source_specific_mode(),
        )

        if report.is_valid:
            return True

        QMessageBox.warning(
            self,
            "Source validation failed",
            report.to_text()
            + "\n\nCorrect the source attributes and run the calculation again.",
        )
        self.tabWidget.setCurrentWidget(self.inputsTab)
        return False

    def calculate_prediction(self) -> None:
        """Calculate cumulative noise from all selected sources at each receptor."""

        if not self._validate_inputs():
            return

        source_layer = self.sourceLayerCombo.currentLayer()
        receptor_layer = self.receptorLayerCombo.currentLayer()

        if source_layer is None or receptor_layer is None:
            QMessageBox.warning(
                self, "Layers required",
                "Select both a source point layer and a receptor point layer."
            )
            return

        source_features = list(source_layer.getSelectedFeatures())
        if not source_features:
            QMessageBox.warning(
                self, "Select sources",
                "Select one or more source points with the QGIS selection tool."
            )
            return

        if receptor_layer.featureCount() == 0:
            QMessageBox.warning(self, "No receptors", "The receptor layer is empty.")
            return

        try:
            source_models = [
                self._source_model_from_feature(feature)
                for feature in source_features
            ]

            if not self._validate_source_models(source_models):
                return

            self.resultsTable.setRowCount(0)
            self._current_output_layer = None
            self._current_receptor_layer = receptor_layer
            self._set_results_actions_enabled(False)
            prediction_records = []
            errors = []
            first_record = None

            for receptor_feature in receptor_layer.getFeatures():
                try:
                    receptor_point = self._point_from_feature(receptor_feature)
                    contributions = []

                    for source in source_models:
                        distance_m = self._measure_distance_metres(
                            source.geometry,
                            receptor_point,
                            source_layer,
                            receptor_layer,
                        )
                        result = predict_noise_level(PredictionInput(
                            source_level_db=source.level_db,
                            distance_m=distance_m,
                            ground_type=source.ground_type,
                            soft_ground_percent=self.softGroundSpin.value(),
                            screening_type=source.screening,
                            reflection_correction_db=source.reflection_db,
                            activity_duration_hours=source.duration_hours,
                            assessment_duration_hours=self.assessmentDurationSpin.value(),
                        ))
                        contributions.append((source, result))

                    combined_level = round(
                        logarithmic_sum(
                            result.predicted_level_db
                            for _, result in contributions
                        ),
                        1,
                    )
                    dominant_source, dominant_result = max(
                        contributions,
                        key=lambda item: item[1].predicted_level_db,
                    )
                    nearest_distance = min(
                        result.distance_m for _, result in contributions
                    )

                    record = {
                        "receptor_feature": receptor_feature,
                        "source_count": len(contributions),
                        "nearest_distance_m": round(nearest_distance, 1),
                        "dominant_source_id": dominant_source.source_id,
                        "dominant_source_fid": dominant_source.feature_id,
                        "dominant_source_level_db": round(
                            dominant_source.level_db, 1
                        ),
                        "minimum_source_level_db": round(
                            min(source.level_db for source, _ in contributions),
                            1,
                        ),
                        "maximum_source_level_db": round(
                            max(source.level_db for source, _ in contributions),
                            1,
                        ),
                        "dominant_activity": dominant_source.activity,
                        "dominant_equipment": dominant_source.equipment,
                        "dominant_duration_hours": dominant_source.duration_hours,
                        "dominant_ground": dominant_source.ground_type.value,
                        "dominant_screening": dominant_source.screening.value,
                        "dominant_reflection_db": dominant_source.reflection_db,
                        "dominant_result": round_result(
                            dominant_result, decimals=1
                        ),
                        "combined_level_db": combined_level,
                    }
                    prediction_records.append(record)
                    self._add_result_row(record)
                    if first_record is None:
                        first_record = record

                except Exception as error:
                    errors.append(f"Receptor {receptor_feature.id()}: {error}")

            if not prediction_records:
                raise ValueError("No receptor predictions were completed.")

            output_layer = self._create_output_layer(
                source_features=source_features,
                receptor_layer=receptor_layer,
                prediction_records=prediction_records,
            )

            self._current_output_layer = output_layer
            self._set_results_actions_enabled(True)
            if self.resultsTable.rowCount() > 0:
                self.resultsTable.selectRow(0)

            self._show_summary_result(first_record)
            self.distanceSpin.setValue(first_record["nearest_distance_m"])
            self.tabWidget.setCurrentWidget(self.resultsTab)

            message = (
                f"Completed cumulative predictions from {len(source_features)} "
                f"source(s) for {len(prediction_records)} receptor(s)."
                f"\n\nCreated output: {output_layer.name()}"
            )
            if self.permanentOutputRadio.isChecked():
                message += f"\nSaved to: {self.outputPathEdit.text().strip()}"
            if errors:
                message += f"\n\nSkipped {len(errors)} receptor(s) with errors."

            QMessageBox.information(self, "Prediction complete", message)
        except ValueError as error:
            QMessageBox.warning(self, "Calculation error", str(error))
        except Exception as error:
            QMessageBox.critical(
                self, "Unexpected error",
                f"The cumulative prediction could not be completed.\n\nDetails: {error}"
            )

    def _create_output_layer(
        self,
        source_features,
        receptor_layer: QgsVectorLayer,
        prediction_records,
    ) -> QgsVectorLayer:
        """Create the cumulative receptor output layer."""

        requested_name = self.outputLayerNameEdit.text().strip()
        layer_name = self._unique_output_layer_name(requested_name)
        memory_layer = self._build_memory_output_layer(
            source_features, receptor_layer, prediction_records, layer_name
        )

        if self.applySymbologyCheck.isChecked():
            self._apply_noise_symbology(memory_layer)

        if self.temporaryOutputRadio.isChecked():
            if self.addToProjectCheck.isChecked():
                QgsProject.instance().addMapLayer(memory_layer)
            return memory_layer

        output_path = os.path.normpath(self.outputPathEdit.text().strip())
        if self.shapefileOutputRadio.isChecked():
            saved_layer = self._save_to_shapefile(
                memory_layer, output_path, requested_name
            )
        else:
            saved_layer = self._save_to_geopackage(
                memory_layer, output_path, requested_name
            )
        if self.applySymbologyCheck.isChecked():
            self._apply_noise_symbology(saved_layer)
        if self.addToProjectCheck.isChecked():
            QgsProject.instance().addMapLayer(saved_layer)
        return saved_layer

    def _build_memory_output_layer(
        self,
        source_features,
        receptor_layer: QgsVectorLayer,
        prediction_records,
        layer_name: str,
    ) -> QgsVectorLayer:
        geometry_name = QgsWkbTypes.displayString(receptor_layer.wkbType())
        crs_authid = receptor_layer.crs().authid()
        output_layer = QgsVectorLayer(
            f"{geometry_name}?crs={crs_authid}", layer_name, "memory"
        )
        if not output_layer.isValid():
            raise ValueError("Could not create the cumulative prediction layer.")

        provider = output_layer.dataProvider()
        provider.addAttributes([
            QgsField("receptor_id", QVariant.String, len=80),
            QgsField("receptor_fid", QVariant.LongLong),
            QgsField("source_cnt", QVariant.Int),
            QgsField("near_dist_m", QVariant.Double, len=20, prec=1),
            QgsField("dominant_id", QVariant.String, len=80),
            QgsField("dominant_fid", QVariant.LongLong),
            QgsField("dominant_db", QVariant.Double, len=10, prec=1),
            QgsField("combined_db", QVariant.Double, len=10, prec=1),
            QgsField("dom_src_db", QVariant.Double, len=10, prec=1),
            QgsField("src_min_db", QVariant.Double, len=10, prec=1),
            QgsField("src_max_db", QVariant.Double, len=10, prec=1),
            QgsField("level_field", QVariant.String, len=80),
            QgsField("ground_type", QVariant.String, len=20),
            QgsField("screening", QVariant.String, len=20),
        ])
        output_layer.updateFields()

        output_features = []
        for record in prediction_records:
            receptor_feature = record["receptor_feature"]
            dominant_result = record["dominant_result"]
            output_feature = QgsFeature(output_layer.fields())
            output_feature.setGeometry(receptor_feature.geometry())
            output_feature.setAttributes([
                self._receptor_identifier(receptor_feature),
                int(receptor_feature.id()),
                record["source_count"],
                record["nearest_distance_m"],
                record["dominant_source_id"],
                record["dominant_source_fid"],
                dominant_result.predicted_level_db,
                record["combined_level_db"],
                record["dominant_source_level_db"],
                record["minimum_source_level_db"],
                record["maximum_source_level_db"],
                (self.sourceLevelFieldCombo.currentField()
                 if self._uses_source_level_field() else "<common value>"),
                self._selected_ground_type().value,
                self._selected_screening_type().value,
            ])
            output_features.append(output_feature)

        if not provider.addFeatures(output_features):
            raise ValueError("Could not write cumulative prediction features.")
        output_layer.updateExtents()
        return output_layer

    def _save_to_geopackage(
        self,
        source_layer: QgsVectorLayer,
        output_path: str,
        requested_layer_name: str,
    ) -> QgsVectorLayer:
        output_directory = os.path.dirname(output_path)
        if output_directory and not os.path.isdir(output_directory):
            os.makedirs(output_directory, exist_ok=True)

        gpkg_layer_name = self._safe_geopackage_layer_name(requested_layer_name)
        options = QgsVectorFileWriter.SaveVectorOptions()
        options.driverName = "GPKG"
        options.layerName = gpkg_layer_name
        options.fileEncoding = "UTF-8"

        if os.path.exists(output_path):
            options.actionOnExistingFile = (
                QgsVectorFileWriter.CreateOrOverwriteLayer
            )
        else:
            options.actionOnExistingFile = (
                QgsVectorFileWriter.CreateOrOverwriteFile
            )

        result = QgsVectorFileWriter.writeAsVectorFormatV3(
            source_layer,
            output_path,
            QgsProject.instance().transformContext(),
            options,
        )
        error_code = result[0] if isinstance(result, tuple) else result
        if error_code != QgsVectorFileWriter.NoError:
            error_message = result[1] if isinstance(result, tuple) and len(result) > 1 else ""
            raise ValueError(
                "Could not save the GeoPackage output."
                + (f"\n\nDetails: {error_message}" if error_message else "")
            )

        saved_layer = QgsVectorLayer(
            f"{output_path}|layername={gpkg_layer_name}",
            requested_layer_name,
            "ogr",
        )
        if not saved_layer.isValid():
            raise ValueError(
                "The GeoPackage was written, but QGIS could not load the output layer."
            )
        return saved_layer

    def _save_to_shapefile(
        self,
        source_layer: QgsVectorLayer,
        output_path: str,
        requested_layer_name: str,
    ) -> QgsVectorLayer:
        """Write the prediction output as an ESRI Shapefile."""

        output_directory = os.path.dirname(output_path)
        if output_directory and not os.path.isdir(output_directory):
            os.makedirs(output_directory, exist_ok=True)

        options = QgsVectorFileWriter.SaveVectorOptions()
        options.driverName = "ESRI Shapefile"
        options.fileEncoding = "UTF-8"
        options.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteFile

        result = QgsVectorFileWriter.writeAsVectorFormatV3(
            source_layer,
            output_path,
            QgsProject.instance().transformContext(),
            options,
        )
        error_code = result[0] if isinstance(result, tuple) else result
        if error_code != QgsVectorFileWriter.NoError:
            error_message = (
                result[1]
                if isinstance(result, tuple) and len(result) > 1
                else ""
            )
            raise ValueError(
                "Could not save the Shapefile output."
                + (f"\n\nDetails: {error_message}" if error_message else "")
            )

        saved_layer = QgsVectorLayer(output_path, requested_layer_name, "ogr")
        if not saved_layer.isValid():
            raise ValueError(
                "The Shapefile was written, but QGIS could not load it."
            )
        return saved_layer

    @staticmethod
    def _safe_geopackage_layer_name(name: str) -> str:
        cleaned = re.sub(r"[^A-Za-z0-9_]+", "_", name.strip())
        cleaned = cleaned.strip("_") or "noise_prediction_results"
        if cleaned[0].isdigit():
            cleaned = f"noise_{cleaned}"
        return cleaned[:63]

    @staticmethod
    def _unique_output_layer_name(base_name: str) -> str:
        project = QgsProject.instance()
        existing_names = {layer.name() for layer in project.mapLayers().values()}
        if base_name not in existing_names:
            return base_name

        counter = 2
        while f"{base_name} ({counter})" in existing_names:
            counter += 1
        return f"{base_name} ({counter})"

    @staticmethod
    def _apply_noise_symbology(layer: QgsVectorLayer) -> None:
        bands = [
            (0.0, 45.0, "Below 45 dB", "#2ca25f"),
            (45.0, 55.0, "45–55 dB", "#99d8c9"),
            (55.0, 65.0, "55–65 dB", "#fee08b"),
            (65.0, 75.0, "65–75 dB", "#fc8d59"),
            (75.0, 200.0, "75 dB and above", "#d73027"),
        ]

        ranges = []
        for lower, upper, label, colour in bands:
            symbol = QgsMarkerSymbol.createSimple({
                "name": "circle",
                "color": colour,
                "outline_color": "#333333",
                "outline_width": "0.3",
                "size": "4.0",
            })
            ranges.append(QgsRendererRange(lower, upper, symbol, label))

        renderer = QgsGraduatedSymbolRenderer("combined_db", ranges)
        renderer.setMode(QgsGraduatedSymbolRenderer.Custom)
        layer.setRenderer(renderer)
        layer.triggerRepaint()

    def _add_result_row(self, record) -> None:
        row = self.resultsTable.rowCount()
        self.resultsTable.insertRow(row)
        receptor_feature = record["receptor_feature"]
        dominant_result = record["dominant_result"]
        values = [
            self._receptor_identifier(receptor_feature),
            str(record["source_count"]),
            f'{record["nearest_distance_m"]:.1f}',
            record["dominant_source_id"],
            f'{record["dominant_source_level_db"]:.1f}',
            f"{dominant_result.predicted_level_db:.1f}",
            f'{record["combined_level_db"]:.1f}',
        ]
        for column, value in enumerate(values):
            item = QTableWidgetItem(value)
            if column in (1, 2, 4, 5, 6):
                item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            item.setData(Qt.UserRole, receptor_feature.id())
            self.resultsTable.setItem(row, column, item)

    def _set_results_actions_enabled(self, enabled: bool) -> None:
        """Enable or disable table-to-map and export actions."""

        self.selectReceptorButton.setEnabled(enabled)
        self.zoomReceptorButton.setEnabled(enabled)
        self.exportCsvButton.setEnabled(enabled)

    def _selected_receptor_fid(self):
        """Return the original receptor feature ID for the selected row."""

        row = self.resultsTable.currentRow()
        if row < 0:
            return None

        item = self.resultsTable.item(row, 0)
        if item is None:
            return None

        return item.data(Qt.UserRole)

    def _on_result_selection_changed(self) -> None:
        """Select the corresponding receptor whenever a table row is clicked."""

        if self._selected_receptor_fid() is not None:
            self._select_receptor_from_table(show_warning=False)

    def _select_receptor_from_table(self, *args, show_warning: bool = True) -> bool:
        """Select the table receptor in the output and original layers."""

        receptor_fid = self._selected_receptor_fid()
        if receptor_fid is None:
            if show_warning:
                QMessageBox.information(
                    self,
                    "Select a result",
                    "Select one receptor row in the results table.",
                )
            return False

        selected = False
        output_layer = self._current_output_layer
        if output_layer is not None and output_layer.isValid():
            expression = f'"receptor_fid" = {int(receptor_fid)}'
            output_ids = [
                feature.id()
                for feature in output_layer.getFeatures(
                    QgsFeatureRequest().setFilterExpression(expression)
                )
            ]
            output_layer.selectByIds(output_ids)
            if output_ids:
                selected = True
                if QgsProject.instance().mapLayer(output_layer.id()) is not None:
                    iface.setActiveLayer(output_layer)

        receptor_layer = self._current_receptor_layer
        if receptor_layer is not None and receptor_layer.isValid():
            receptor_layer.selectByIds([int(receptor_fid)])
            selected = True
            if output_layer is None or QgsProject.instance().mapLayer(
                output_layer.id()
            ) is None:
                iface.setActiveLayer(receptor_layer)

        if selected:
            iface.mapCanvas().refresh()
            return True

        if show_warning:
            QMessageBox.warning(
                self,
                "Receptor unavailable",
                "The selected receptor could not be found in the current layers.",
            )
        return False

    def _zoom_to_selected_receptor(self, *args) -> None:
        """Select and zoom the map canvas to the current result receptor."""

        if not self._select_receptor_from_table(show_warning=True):
            return

        output_layer = self._current_output_layer
        if (
            output_layer is not None
            and output_layer.isValid()
            and QgsProject.instance().mapLayer(output_layer.id()) is not None
            and output_layer.selectedFeatureCount() > 0
        ):
            iface.mapCanvas().zoomToSelected(output_layer)
        elif (
            self._current_receptor_layer is not None
            and self._current_receptor_layer.selectedFeatureCount() > 0
        ):
            iface.mapCanvas().zoomToSelected(self._current_receptor_layer)

        iface.mapCanvas().refresh()

    def _export_results_csv(self) -> None:
        """Export the visible receptor prediction results to CSV."""

        if self.resultsTable.rowCount() == 0:
            QMessageBox.information(
                self,
                "No results",
                "Run a prediction before exporting the results.",
            )
            return

        project_path = QgsProject.instance().homePath() or os.path.expanduser("~")
        default_name = self._safe_geopackage_layer_name(
            self.outputLayerNameEdit.text().strip()
        )
        start_path = os.path.join(project_path, f"{default_name}.csv")

        csv_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export prediction results",
            start_path,
            "CSV files (*.csv)",
        )
        if not csv_path:
            return
        if not csv_path.lower().endswith(".csv"):
            csv_path += ".csv"

        try:
            with open(csv_path, "w", newline="", encoding="utf-8-sig") as stream:
                writer = csv.writer(stream)
                writer.writerow([
                    self.resultsTable.horizontalHeaderItem(column).text()
                    for column in range(self.resultsTable.columnCount())
                ])
                for row in range(self.resultsTable.rowCount()):
                    writer.writerow([
                        self.resultsTable.item(row, column).text()
                        if self.resultsTable.item(row, column) is not None else ""
                        for column in range(self.resultsTable.columnCount())
                    ])
        except OSError as error:
            QMessageBox.critical(
                self,
                "CSV export failed",
                f"The results could not be exported.\n\nDetails: {error}",
            )
            return

        QMessageBox.information(
            self,
            "CSV export complete",
            f"The prediction results were exported to:\n{csv_path}",
        )

    def _show_summary_result(self, record) -> None:
        """Show the dominant contribution and cumulative level for one receptor."""

        result = record["dominant_result"]
        self.distanceResultLabel.setText(f"−{result.distance_attenuation_db:.1f} dB")
        self.groundResultLabel.setText(f"−{result.ground_attenuation_db:.1f} dB")
        self.screeningResultLabel.setText(f"−{result.screening_attenuation_db:.1f} dB")
        self.reflectionResultLabel.setText(f"+{result.reflection_correction_db:.1f} dB")
        self.durationResultLabel.setText(f"{result.duration_correction_db:+.1f} dB")
        self.beforeDurationResultLabel.setText(
            f'Dominant source {record["dominant_source_id"]}: '
            f"{result.predicted_level_db:.1f} dB"
        )
        self.predictedResultLabel.setText(
            f'{record["combined_level_db"]:.1f} dB'
        )

    @staticmethod
    def _point_from_feature(feature: QgsFeature):
        geometry = feature.geometry()
        if geometry is None or geometry.isEmpty():
            raise ValueError(f"Feature {feature.id()} has empty geometry.")
        if QgsWkbTypes.geometryType(geometry.wkbType()) != Qgis.GeometryType.Point:
            raise ValueError(f"Feature {feature.id()} is not a point feature.")
        if geometry.isMultipart():
            points = geometry.asMultiPoint()
            if not points:
                raise ValueError(f"Feature {feature.id()} has no valid point.")
            return points[0]
        return geometry.asPoint()

    @staticmethod
    def _source_identifier(feature: QgsFeature) -> str:
        for field_name in ("source_id", "plant_id", "name", "id", "ID"):
            if field_name in feature.fields().names():
                value = feature[field_name]
                if value not in (None, ""):
                    return str(value)
        return str(feature.id())

    @staticmethod
    def _receptor_identifier(feature: QgsFeature) -> str:
        for field_name in ("receptor_id", "site_id", "name", "id", "ID"):
            if field_name in feature.fields().names():
                value = feature[field_name]
                if value not in (None, ""):
                    return str(value)
        return str(feature.id())

    @staticmethod
    def _measure_distance_metres(
        source_point, receptor_point,
        source_layer: QgsVectorLayer,
        receptor_layer: QgsVectorLayer,
    ) -> float:
        project = QgsProject.instance()
        transformed_receptor = receptor_point
        if source_layer.crs() != receptor_layer.crs():
            transform = QgsCoordinateTransform(
                receptor_layer.crs(), source_layer.crs(), project.transformContext()
            )
            transformed_receptor = transform.transform(receptor_point)

        distance_area = QgsDistanceArea()
        distance_area.setSourceCrs(source_layer.crs(), project.transformContext())
        if project.ellipsoid():
            distance_area.setEllipsoid(project.ellipsoid())
        distance_m = distance_area.measureLine(source_point, transformed_receptor)
        if distance_m <= 0:
            raise ValueError("Source and receptor cannot occupy the same location.")
        return distance_m

    def _clear_results(self) -> None:
        for label in (
            self.distanceResultLabel, self.groundResultLabel,
            self.screeningResultLabel, self.reflectionResultLabel,
            self.durationResultLabel, self.beforeDurationResultLabel,
            self.predictedResultLabel,
        ):
            label.setText("—")
        self.resultsTable.setRowCount(0)
        self._set_results_actions_enabled(False)

    def reset_form(self) -> None:
        self.simpleModeRadio.setChecked(True)
        self.sourceLevelModeCombo.setCurrentIndex(0)
        self.sourceLevelSpin.setValue(90.0)
        self.distanceSpin.setValue(100.0)
        self.groundCombo.setCurrentIndex(0)
        self.softGroundSpin.setValue(50.0)
        self.screeningCombo.setCurrentIndex(0)
        self.reflectionSpin.setValue(0.0)
        self.assessmentDurationSpin.setValue(8.0)
        self.activityDurationSpin.setValue(4.0)
        self.outputLayerNameEdit.setText("Noise prediction results")
        self.temporaryOutputRadio.setChecked(True)
        self.shapefileOutputRadio.setChecked(False)
        self.outputPathEdit.clear()
        self.addToProjectCheck.setChecked(True)
        self.applySymbologyCheck.setChecked(True)
        self._update_calculation_mode()
        self._update_ground_controls()
        self._update_source_level_controls()
        self._update_source_specific_controls()
        self._update_output_controls()
        self._current_output_layer = None
        self._current_receptor_layer = None
        self._clear_results()
        self._update_layer_status()
        self.tabWidget.setCurrentWidget(self.inputsTab)
