# -*- coding: utf-8 -*-
from __future__ import annotations

import os

from qgis.PyQt import uic
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QHeaderView,
    QMessageBox,
    QTableWidgetItem,
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

from ..core.bs5228_engine import (
    GroundType,
    PredictionInput,
    ScreeningType,
    predict_noise_level,
    round_result,
)

FORM_CLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "noise_prediction_dialog.ui")
)


class NoisePredictionDialog(QDialog, FORM_CLASS):
    """Qt Designer based BS 5228 prediction dialog."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self._connected_source_layer = None
        self._configure_widgets()
        self._populate_choices()
        self._connect_signals()
        self._update_ground_controls()
        self._update_layer_status()
        self._clear_results()

    def _configure_widgets(self) -> None:
        self.sourceLayerCombo.setFilters(QgsMapLayerProxyModel.Filter.PointLayer)
        self.sourceLayerCombo.setAllowEmptyLayer(True)
        self.receptorLayerCombo.setFilters(QgsMapLayerProxyModel.Filter.PointLayer)
        self.receptorLayerCombo.setAllowEmptyLayer(True)

        self.resultsTable.setColumnCount(8)
        self.resultsTable.setHorizontalHeaderLabels([
            "Receptor ID", "Distance (m)", "Distance Att. (dB)",
            "Ground Att. (dB)", "Screening (dB)", "Reflection (dB)",
            "Duration (dB)", "Predicted Level (dB)",
        ])
        self.resultsTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.resultsTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.resultsTable.setAlternatingRowColors(True)
        self.resultsTable.verticalHeader().setVisible(False)
        header = self.resultsTable.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setStretchLastSection(True)

    def _populate_choices(self) -> None:
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
        self.groundCombo.currentIndexChanged.connect(self._update_ground_controls)
        self.sourceLayerCombo.layerChanged.connect(self._on_source_layer_changed)
        self.receptorLayerCombo.layerChanged.connect(self._update_layer_status)
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
        if layer is not None:
            try:
                layer.selectionChanged.connect(self._update_layer_status)
            except (AttributeError, TypeError):
                pass
        self._update_layer_status()

    def _selected_ground_type(self) -> GroundType:
        return self.groundCombo.currentData()

    def _selected_screening_type(self) -> ScreeningType:
        return self.screeningCombo.currentData()

    def _update_ground_controls(self, *args) -> None:
        self.softGroundSpin.setEnabled(
            self._selected_ground_type() == GroundType.MIXED
        )

    def _update_layer_status(self, *args) -> None:
        source_layer = self.sourceLayerCombo.currentLayer()
        receptor_layer = self.receptorLayerCombo.currentLayer()

        if source_layer is None:
            self.sourceStatusLabel.setText("No source layer selected.")
        else:
            count = source_layer.selectedFeatureCount()
            if count == 0:
                self.sourceStatusLabel.setText(
                    "No source selected. Select exactly one source point in QGIS."
                )
            elif count == 1:
                feature = next(source_layer.getSelectedFeatures())
                self.sourceStatusLabel.setText(
                    f"Source feature selected: {feature.id()}"
                )
            else:
                self.sourceStatusLabel.setText(
                    f"{count} source features selected. Keep only one selected."
                )

        if receptor_layer is None:
            self.receptorStatusLabel.setText("No receptor layer selected.")
        else:
            self.receptorStatusLabel.setText(
                f"{receptor_layer.featureCount()} receptor feature(s) available."
            )

    def _validate_inputs(self) -> bool:
        if self.activityDurationSpin.value() > self.assessmentDurationSpin.value():
            QMessageBox.warning(
                self, "Invalid duration",
                "Activity operating time cannot exceed the assessment period."
            )
            self.activityDurationSpin.setFocus()
            return False
        return True

    def calculate_prediction(self) -> None:
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
        if source_layer.selectedFeatureCount() != 1:
            QMessageBox.warning(
                self, "Select one source",
                "Select exactly one source point with the QGIS selection tool."
            )
            return
        if receptor_layer.featureCount() == 0:
            QMessageBox.warning(self, "No receptors", "The receptor layer is empty.")
            return

        try:
            source_feature = next(source_layer.getSelectedFeatures())
            source_point = self._point_from_feature(source_feature)
            self.resultsTable.setRowCount(0)
            first_result = None
            successful_count = 0

            for receptor_feature in receptor_layer.getFeatures():
                receptor_point = self._point_from_feature(receptor_feature)
                distance_m = self._measure_distance_metres(
                    source_point, receptor_point, source_layer, receptor_layer
                )
                result = round_result(predict_noise_level(PredictionInput(
                    source_level_db=self.sourceLevelSpin.value(),
                    distance_m=distance_m,
                    ground_type=self._selected_ground_type(),
                    soft_ground_percent=self.softGroundSpin.value(),
                    screening_type=self._selected_screening_type(),
                    reflection_correction_db=self.reflectionSpin.value(),
                    activity_duration_hours=self.activityDurationSpin.value(),
                    assessment_duration_hours=self.assessmentDurationSpin.value(),
                )), decimals=1)

                if first_result is None:
                    first_result = result
                self._add_result_row(receptor_feature, result)
                successful_count += 1

            if first_result is not None:
                self._show_summary_result(first_result)
                self.distanceSpin.setValue(first_result.distance_m)
                self.tabWidget.setCurrentWidget(self.resultsTab)

            QMessageBox.information(
                self, "Prediction complete",
                f"Completed predictions for {successful_count} receptor(s)."
            )
        except ValueError as error:
            QMessageBox.warning(self, "Calculation error", str(error))
        except Exception as error:
            QMessageBox.critical(
                self, "Unexpected error",
                f"The spatial prediction could not be completed.\n\nDetails: {error}"
            )

    def _add_result_row(self, receptor_feature: QgsFeature, result) -> None:
        row = self.resultsTable.rowCount()
        self.resultsTable.insertRow(row)
        values = [
            self._receptor_identifier(receptor_feature),
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
                item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            item.setData(Qt.UserRole, receptor_feature.id())
            self.resultsTable.setItem(row, column, item)

    def _show_summary_result(self, result) -> None:
        self.distanceResultLabel.setText(f"−{result.distance_attenuation_db:.1f} dB")
        self.groundResultLabel.setText(f"−{result.ground_attenuation_db:.1f} dB")
        self.screeningResultLabel.setText(f"−{result.screening_attenuation_db:.1f} dB")
        self.reflectionResultLabel.setText(f"+{result.reflection_correction_db:.1f} dB")
        self.durationResultLabel.setText(f"{result.duration_correction_db:+.1f} dB")
        self.beforeDurationResultLabel.setText(f"{result.level_before_duration_db:.1f} dB")
        self.predictedResultLabel.setText(f"{result.predicted_level_db:.1f} dB")

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

    def reset_form(self) -> None:
        self.sourceLevelSpin.setValue(90.0)
        self.distanceSpin.setValue(100.0)
        self.groundCombo.setCurrentIndex(0)
        self.softGroundSpin.setValue(50.0)
        self.screeningCombo.setCurrentIndex(0)
        self.reflectionSpin.setValue(0.0)
        self.assessmentDurationSpin.setValue(8.0)
        self.activityDurationSpin.setValue(4.0)
        self._update_ground_controls()
        self._clear_results()
        self._update_layer_status()
        self.tabWidget.setCurrentWidget(self.inputsTab)
