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
        self._configure_widgets()
        self._populate_choices()
        self._connect_signals()
        self._update_ground_controls()
        self._update_output_controls()
        self._update_layer_status()
        self._clear_results()

    def _configure_widgets(self) -> None:
        self.sourceLayerCombo.setFilters(QgsMapLayerProxyModel.Filter.PointLayer)
        self.sourceLayerCombo.setAllowEmptyLayer(True)
        self.receptorLayerCombo.setFilters(QgsMapLayerProxyModel.Filter.PointLayer)
        self.receptorLayerCombo.setAllowEmptyLayer(True)

        self.resultsTable.setColumnCount(6)
        self.resultsTable.setHorizontalHeaderLabels([
            "Receptor ID", "Source Count", "Nearest Distance (m)",
            "Dominant Source", "Highest Contribution (dB)",
            "Combined Level (dB)",
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
        self.temporaryOutputRadio.toggled.connect(self._update_output_controls)
        self.permanentOutputRadio.toggled.connect(self._update_output_controls)
        self.browseOutputButton.clicked.connect(self._browse_output_file)
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

    def _update_output_controls(self, *args) -> None:
        permanent = self.permanentOutputRadio.isChecked()
        self.outputPathEdit.setEnabled(permanent)
        self.browseOutputButton.setEnabled(permanent)

    def _browse_output_file(self) -> None:
        start_path = self.outputPathEdit.text().strip()
        if not start_path:
            project_path = QgsProject.instance().homePath()
            start_path = project_path or os.path.expanduser("~")

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save prediction output",
            start_path,
            "GeoPackage (*.gpkg)",
        )
        if path:
            if not path.lower().endswith(".gpkg"):
                path += ".gpkg"
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
        if self.activityDurationSpin.value() > self.assessmentDurationSpin.value():
            QMessageBox.warning(
                self, "Invalid duration",
                "Activity operating time cannot exceed the assessment period."
            )
            self.activityDurationSpin.setFocus()
            return False

        if not self.outputLayerNameEdit.text().strip():
            QMessageBox.warning(
                self,
                "Output name required",
                "Enter an output layer name.",
            )
            self.outputLayerNameEdit.setFocus()
            return False

        if self.permanentOutputRadio.isChecked():
            output_path = self.outputPathEdit.text().strip()
            if not output_path:
                QMessageBox.warning(
                    self,
                    "Output file required",
                    "Select a GeoPackage file for the permanent output.",
                )
                self.outputPathEdit.setFocus()
                return False
            if not output_path.lower().endswith(".gpkg"):
                QMessageBox.warning(
                    self,
                    "Invalid output file",
                    "The permanent output must use the .gpkg extension.",
                )
                self.outputPathEdit.setFocus()
                return False

        return True

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
            source_records = [
                (feature, self._point_from_feature(feature))
                for feature in source_features
            ]

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

                    for source_feature, source_point in source_records:
                        distance_m = self._measure_distance_metres(
                            source_point, receptor_point, source_layer, receptor_layer
                        )
                        result = predict_noise_level(PredictionInput(
                            source_level_db=self.sourceLevelSpin.value(),
                            distance_m=distance_m,
                            ground_type=self._selected_ground_type(),
                            soft_ground_percent=self.softGroundSpin.value(),
                            screening_type=self._selected_screening_type(),
                            reflection_correction_db=self.reflectionSpin.value(),
                            activity_duration_hours=self.activityDurationSpin.value(),
                            assessment_duration_hours=self.assessmentDurationSpin.value(),
                        ))
                        contributions.append((source_feature, result))

                    combined_level = round(
                        logarithmic_sum(
                            result.predicted_level_db
                            for _, result in contributions
                        ),
                        1,
                    )
                    dominant_source, dominant_result = max(
                        contributions, key=lambda item: item[1].predicted_level_db
                    )
                    nearest_distance = min(
                        result.distance_m for _, result in contributions
                    )

                    record = {
                        "receptor_feature": receptor_feature,
                        "source_count": len(contributions),
                        "nearest_distance_m": round(nearest_distance, 1),
                        "dominant_source_id": self._source_identifier(dominant_source),
                        "dominant_source_fid": int(dominant_source.id()),
                        "dominant_result": round_result(dominant_result, decimals=1),
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
            QgsField("source_db", QVariant.Double, len=10, prec=1),
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
                self.sourceLevelSpin.value(),
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
            f"{dominant_result.predicted_level_db:.1f}",
            f'{record["combined_level_db"]:.1f}',
        ]
        for column, value in enumerate(values):
            item = QTableWidgetItem(value)
            if column in (1, 2, 4, 5):
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
        self.outputPathEdit.clear()
        self.addToProjectCheck.setChecked(True)
        self.applySymbologyCheck.setChecked(True)
        self._update_ground_controls()
        self._update_output_controls()
        self._current_output_layer = None
        self._current_receptor_layer = None
        self._clear_results()
        self._update_layer_status()
        self.tabWidget.setCurrentWidget(self.inputsTab)
