# -*- coding: utf-8 -*-
"""
===============================================================================
Noise Prediction — Construction Noise Assessment
QGIS Plugin
===============================================================================

Author      : Htet Arkar Soe
Copyright   : (C) 2022–2026 Htet Arkar Soe
Version     : 1.2.0-beta
Repository  : https://github.com/htet-coder/Noise-Prediction-Algorithm
License     : GNU General Public License v2 or later (GPL-2.0-or-later)

Description
-----------
A QGIS plugin for predicting construction noise at receptor locations using
a simplified BS 5228-inspired methodology.

Current Features
----------------
• Cumulative noise prediction from multiple construction sources
• Distance attenuation
• Ground attenuation
• Manual screening correction
• Manual reflection correction
• Temporary and permanent output layers
• Sample dataset loader

Notes
-----
This plugin is intended for preliminary construction noise assessments.
It is not an official implementation of BS 5228 and should not be used as
a substitute for detailed acoustic modelling where such analyses are required.

===============================================================================
"""
from __future__ import annotations

import csv
import os
import re

from qgis.PyQt import uic
from qgis.PyQt.QtGui import QDesktopServices
from qgis.PyQt.QtCore import Qt, QVariant, QUrl
from qgis.PyQt.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QScrollArea,
    QSpacerItem,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
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
        self.setWindowTitle(
            "Noise Prediction — Construction Noise Assessment (v1.2.0 Beta)"
        )

        if hasattr(self, "titleLabel"):
            self.titleLabel.setText("Construction Noise Prediction")

        if hasattr(self, "subtitleLabel"):
            self.subtitleLabel.setText(
                "Cumulative construction noise prediction using a simplified BS 5228-inspired methodology."
            )

        if hasattr(self, "versionLabel"):
            self.versionLabel.setText(
                "Version 1.2.0 Beta | © 2026 Htet Arkar Soe"
            )

        self._setup_help_tab()

        self._connected_source_layer = None
        self._current_output_layer = None
        self._current_receptor_layer = None
        self._prediction_records_by_receptor = {}
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


    def _setup_help_tab(self) -> None:
        """Create a scrollable Help, support, and professional-services tab."""

        repository_url = (
            "https://github.com/htet-coder/Noise-Prediction-Algorithm/tree/release/1.2.0-beta"
        )
        documentation_url = f"{repository_url}#readme"
        issues_url = f"{repository_url}/issues"

        # Replace these three values with your actual contact details before release.
        contact_email = "htetarkar.env.2016@gmail.com"
        linkedin_url = "https://www.linkedin.com/in/htet-arkar-soe-b58255157/"
        facebook_url = "https://www.facebook.com/htetarkarsoe.50446"

        if hasattr(self, "helpTab"):
            help_tab = self.helpTab
            existing_layout = help_tab.layout()
            if existing_layout is not None:
                while existing_layout.count():
                    item = existing_layout.takeAt(0)
                    widget = item.widget()
                    if widget is not None:
                        widget.deleteLater()
                outer_layout = existing_layout
            else:
                outer_layout = QVBoxLayout(help_tab)
        else:
            help_tab = QWidget(self.tabWidget)
            help_tab.setObjectName("helpTab")
            self.helpTab = help_tab
            outer_layout = QVBoxLayout(help_tab)
            self.tabWidget.addTab(help_tab, "Help")

        tab_index = self.tabWidget.indexOf(help_tab)
        if tab_index >= 0:
            self.tabWidget.setTabText(tab_index, "Help")

        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        scroll_area = QScrollArea(help_tab)
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
        outer_layout.addWidget(scroll_area)

        content = QWidget(scroll_area)
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(24, 20, 24, 24)
        content_layout.setSpacing(14)
        scroll_area.setWidget(content)

        heading = QLabel("Noise Prediction Plugin", content)
        heading.setStyleSheet(
            "font-size: 18px; font-weight: 700; color: #263238;"
        )
        heading.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(heading)

        summary = QLabel(
            "Construction Noise Assessment for QGIS\n"
            "Version 1.2.0 Beta Beta",
            content,
        )
        summary.setAlignment(Qt.AlignmentFlag.AlignCenter)
        summary.setStyleSheet("font-size: 12px; color: #455a64;")
        content_layout.addWidget(summary)

        documentation_group = QGroupBox("Documentation and Support", content)
        documentation_layout = QVBoxLayout(documentation_group)
        help_text = QLabel(
            "The complete installation guide, workflow instructions, sample-data "
            "information, methodology notes, troubleshooting guidance, and release "
            "updates are maintained on the GitHub README page.",
            documentation_group,
        )
        help_text.setWordWrap(True)
        documentation_layout.addWidget(help_text)

        button_layout = QHBoxLayout()
        documentation_button = QPushButton(
            "Open README Documentation", documentation_group
        )
        repository_button = QPushButton(
            "Open GitHub Repository", documentation_group
        )
        issues_button = QPushButton("Report an Issue", documentation_group)
        documentation_button.clicked.connect(
            lambda: self._open_help_url(documentation_url)
        )
        repository_button.clicked.connect(
            lambda: self._open_help_url(repository_url)
        )
        issues_button.clicked.connect(lambda: self._open_help_url(issues_url))
        button_layout.addWidget(documentation_button)
        button_layout.addWidget(repository_button)
        button_layout.addWidget(issues_button)
        documentation_layout.addLayout(button_layout)
        content_layout.addWidget(documentation_group)

        support_group = QGroupBox(
            "Professional Support and Collaboration", content
        )
        support_layout = QVBoxLayout(support_group)
        support_label = QLabel(
            "<p><b>Thank you for using the Noise Prediction Plugin.</b></p>"
            "<p>This tool was developed to support EIA practitioners, consulting "
            "companies, engineering teams, government agencies, NGOs, universities, "
            "and researchers who need a practical and transparent workflow for "
            "preliminary construction-noise assessment in QGIS.</p>"
            "<p>I hope the plugin contributes to more efficient project planning, "
            "environmental assessment, reporting, and evidence-based decision-making.</p>"
            "<p><b>Coaching, mentoring, training, and consulting support is available "
            "for individuals and organizations.</b> This may include project-specific "
            "technical guidance, one-to-one mentoring, team training, construction "
            "noise assessment, GIS-based environmental analysis, environmental "
            "management planning, research collaboration, and customization of GIS "
            "or QGIS tools.</p>",
            support_group,
        )
        support_label.setWordWrap(True)
        support_label.setTextFormat(Qt.TextFormat.RichText)
        support_layout.addWidget(support_label)
        content_layout.addWidget(support_group)

        developer_group = QGroupBox("About the Developer", content)
        developer_layout = QVBoxLayout(developer_group)
        developer_label = QLabel(
            "<p><b>Htet Arkar Soe</b><br>"
            "Environmental Consultant | GIS Specialist | QGIS Plugin Developer</p>"
            "<p>I have several years of professional experience in Environmental "
            "Impact Assessment, GIS, environmental monitoring, spatial analysis, "
            "and organizational capacity development. This plugin was created from "
            "practical consulting experience to make construction-noise assessment "
            "more accessible, transparent, and efficient for environmental "
            "professionals.</p>"
            "<p>The current Version 1.2.0 Beta Beta uses a simplified BS 5228-inspired "
            "methodology for preliminary assessment. Future releases will expand "
            "the calculation workflow, reporting options, source management, and "
            "other functions based on professional requirements and user feedback.</p>",
            developer_group,
        )
        developer_label.setWordWrap(True)
        developer_label.setTextFormat(Qt.TextFormat.RichText)
        developer_layout.addWidget(developer_label)
        content_layout.addWidget(developer_group)

        contact_group = QGroupBox("Contact and Stay Connected", content)
        contact_layout = QVBoxLayout(contact_group)
        contact_label = QLabel(
            "I welcome feedback, collaboration opportunities, consulting enquiries, "
            "training requests, and suggestions for future versions. Follow the "
            "project to receive updates about tutorials, sample data, new tools, "
            "and the future Version 1.0.0 release.",
            contact_group,
        )
        contact_label.setWordWrap(True)
        contact_layout.addWidget(contact_label)

        contact_buttons = QHBoxLayout()
        email_button = QPushButton("Email", contact_group)
        linkedin_button = QPushButton("LinkedIn", contact_group)
        facebook_button = QPushButton("Facebook", contact_group)
        github_button = QPushButton("GitHub", contact_group)

        email_is_configured = contact_email != "your.email@example.com"
        linkedin_is_configured = "your-profile" not in linkedin_url
        facebook_is_configured = "your-profile" not in facebook_url
        email_button.setEnabled(email_is_configured)
        linkedin_button.setEnabled(linkedin_is_configured)
        facebook_button.setEnabled(facebook_is_configured)
        if not email_is_configured:
            email_button.setToolTip(
                "Set contact_email in _setup_help_tab() before publishing."
            )
        if not linkedin_is_configured:
            linkedin_button.setToolTip(
                "Set linkedin_url in _setup_help_tab() before publishing."
            )
        if not facebook_is_configured:
            facebook_button.setToolTip(
                "Set facebook_url in _setup_help_tab() before publishing."
            )

        email_button.clicked.connect(
            lambda: self._open_help_url(f"mailto:{contact_email}")
        )
        linkedin_button.clicked.connect(
            lambda: self._open_help_url(linkedin_url)
        )
        facebook_button.clicked.connect(
            lambda: self._open_help_url(facebook_url)
        )
        github_button.clicked.connect(
            lambda: self._open_help_url(repository_url)
        )
        contact_buttons.addWidget(email_button)
        contact_buttons.addWidget(linkedin_button)
        contact_buttons.addWidget(facebook_button)
        contact_buttons.addWidget(github_button)
        contact_layout.addLayout(contact_buttons)
        content_layout.addWidget(contact_group)

        final_group = QGroupBox("Using the Tool Responsibly", content)
        final_layout = QVBoxLayout(final_group)
        final_label = QLabel(
            "<p>Construction-noise assessment should be more than simply calculating "
            "a predicted sound level.</p>"
            "<p>When applied appropriately, this plugin can support practitioners in "
            "identifying sensitive receptors, evaluating likely project impacts, and "
            "developing <b>impact-based mitigation measures and environmental "
            "management plans</b> that respond to the actual project conditions.</p>"
            "<p>The objective is not to produce generic lists of impacts or mitigation "
            "measures, but to support evidence-based assessment and practical noise "
            "management throughout the project lifecycle.</p>"
            "<p><b>Important:</b> This beta version is intended for preliminary "
            "assessment. It is not an official implementation of BS 5228 and does "
            "not replace professional acoustic judgement or detailed modelling where "
            "those are required.</p>",
            final_group,
        )
        final_label.setWordWrap(True)
        final_label.setTextFormat(Qt.TextFormat.RichText)
        final_layout.addWidget(final_label)
        content_layout.addWidget(final_group)

        footer = QLabel(
            "Noise Prediction Plugin for QGIS | Version 1.2.0 Beta Beta<br>"
            "Developed by Htet Arkar Soe | © 2022–2026<br>"
            "GNU General Public License v2 or later",
            content,
        )
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet("color: #607d8b; font-size: 11px;")
        footer.setTextFormat(Qt.TextFormat.RichText)
        content_layout.addWidget(footer)

    def _open_help_url(self, url: str) -> None:
        """Open a documentation or support URL in the default web browser."""

        if not QDesktopServices.openUrl(QUrl(url)):
            QMessageBox.warning(
                self,
                "Could not open link",
                "The web page could not be opened in your default browser.\n\n"
                f"Address: {url}",
            )

    def _configure_widgets(self) -> None:
        self.sourceLayerCombo.setFilters(QgsMapLayerProxyModel.Filter.PointLayer)
        self.sourceLayerCombo.setAllowEmptyLayer(True)
        self.receptorLayerCombo.setFilters(QgsMapLayerProxyModel.Filter.PointLayer)
        self.receptorLayerCombo.setAllowEmptyLayer(True)

        self.sourceLevelFieldCombo.setFilters(QgsFieldProxyModel.Filter.AllTypes)
        self.sourceLevelFieldCombo.setLayer(self.sourceLayerCombo.currentLayer())

        # Phase 4C source-specific activity attribute fields.
        self.activityFieldCombo.setFilters(QgsFieldProxyModel.Filter.AllTypes)
        self.equipmentFieldCombo.setFilters(QgsFieldProxyModel.Filter.AllTypes)
        # Allow numeric database fields and text fields containing numeric values.
        # Values are converted and validated when SourceModel objects are built.
        self.durationFieldCombo.setFilters(QgsFieldProxyModel.Filter.AllTypes)
        self.groundFieldCombo.setFilters(QgsFieldProxyModel.Filter.AllTypes)
        self.screeningFieldCombo.setFilters(QgsFieldProxyModel.Filter.AllTypes)
        self.reflectionFieldCombo.setFilters(QgsFieldProxyModel.Filter.AllTypes)

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
        self.resultsTable.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.resultsTable.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.resultsTable.setAlternatingRowColors(True)
        self.resultsTable.verticalHeader().setVisible(False)
        header = self.resultsTable.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.setStretchLastSection(True)
        self.resultsTable.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
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
        if hasattr(self, "loadSampleDataButton"):
            self.loadSampleDataButton.clicked.connect(self._load_sample_data)

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

    def _load_sample_data(self) -> None:
        """Load the bundled demonstration source and receptor layers."""

        sample_folder = os.path.normpath(
            os.path.join(
                os.path.dirname(__file__),
                "..",
                "dataset",
                "sample_data_v1.2.0 beta",
            )
        )

        if not os.path.isdir(sample_folder):
            QMessageBox.critical(
                self,
                "Sample data not found",
                "The bundled sample-data folder could not be found.\n\n"
                f"Expected location:\n{sample_folder}",
            )
            return

        source_path = self._find_sample_shapefile(
            sample_folder,
            preferred_names=(
                "Construction_Sources.shp",
                "Construction Sources.shp",
            ),
            keyword="source",
        )
        receptor_path = self._find_sample_shapefile(
            sample_folder,
            preferred_names=(
                "Receptors.shp",
                "Receptor.shp",
            ),
            keyword="receptor",
        )

        if source_path is None or receptor_path is None:
            missing = []
            if source_path is None:
                missing.append("construction source point layer")
            if receptor_path is None:
                missing.append("receptor point layer")
            QMessageBox.critical(
                self,
                "Sample data incomplete",
                "Could not locate the following sample layer(s):\n\n"
                + "\n".join(f"• {item}" for item in missing)
                + f"\n\nChecked folder:\n{sample_folder}",
            )
            return

        source_layer = self._project_layer_for_path(source_path)
        if source_layer is None:
            source_layer = QgsVectorLayer(
                source_path,
                "Construction Sources — Sample",
                "ogr",
            )
            if not source_layer.isValid():
                QMessageBox.critical(
                    self,
                    "Sample source layer error",
                    f"QGIS could not load:\n{source_path}",
                )
                return
            QgsProject.instance().addMapLayer(source_layer)

        receptor_layer = self._project_layer_for_path(receptor_path)
        if receptor_layer is None:
            receptor_layer = QgsVectorLayer(
                receptor_path,
                "Receptors — Sample",
                "ogr",
            )
            if not receptor_layer.isValid():
                QMessageBox.critical(
                    self,
                    "Sample receptor layer error",
                    f"QGIS could not load:\n{receptor_path}",
                )
                return
            QgsProject.instance().addMapLayer(receptor_layer)

        self.sourceLayerCombo.setLayer(source_layer)
        self.receptorLayerCombo.setLayer(receptor_layer)
        self._update_layer_status()

        combined_extent = source_layer.extent()
        combined_extent.combineExtentWith(receptor_layer.extent())
        iface.mapCanvas().setExtent(combined_extent)
        iface.mapCanvas().refresh()

        QMessageBox.information(
            self,
            "Sample data loaded",
            "The bundled construction-source and receptor layers were loaded "
            "successfully.\n\n"
            "No source selection is required: all sources will be calculated "
            "unless you select a subset in QGIS.",
        )

    @staticmethod
    def _find_sample_shapefile(
        folder: str,
        preferred_names,
        keyword: str,
    ):
        """Find a sample shapefile by preferred name, then by keyword."""

        files = {
            name.lower(): os.path.join(folder, name)
            for name in os.listdir(folder)
            if name.lower().endswith(".shp")
        }

        for preferred_name in preferred_names:
            path = files.get(preferred_name.lower())
            if path:
                return os.path.normpath(path)

        matches = [
            path for name, path in files.items()
            if keyword.lower() in name
        ]
        if len(matches) == 1:
            return os.path.normpath(matches[0])
        return None

    @staticmethod
    def _project_layer_for_path(path: str):
        """Return an already-loaded project layer matching a file path."""

        target = os.path.normcase(os.path.abspath(path))
        for layer in QgsProject.instance().mapLayers().values():
            if not isinstance(layer, QgsVectorLayer):
                continue
            layer_source = layer.source().split("|", 1)[0]
            if os.path.normcase(os.path.abspath(layer_source)) == target:
                return layer
        return None

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

        if source_layer.featureCount() == 0:
            QMessageBox.warning(
                self,
                "No sources",
                "The source point layer is empty.",
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
        """Apply the correct soft-ground proportion behaviour.

        Simple mode:
            Hard ground  -> 0% soft ground, control disabled.
            Soft ground  -> 100% soft ground, control disabled.
            Mixed ground -> user-defined proportion, control enabled.

        Source-Specific mode:
            When a ground field is mapped, the shared percentage is enabled
            because it is used only by source features whose mapped value is
            MIXED. HARD and SOFT source features use 0% and 100% respectively.
        """

        specific_mode = self._is_source_specific_mode()
        ground_field_mapped = (
            specific_mode and bool(self.groundFieldCombo.currentField())
        )

        if ground_field_mapped:
            self.softGroundSpin.setEnabled(True)
            self.softGroundSpin.setToolTip(
                "Used only for source features whose mapped ground value is MIXED. "
                "HARD sources use 0% and SOFT sources use 100% automatically."
            )
            return

        ground_type = self._selected_ground_type()

        if ground_type == GroundType.HARD:
            self.softGroundSpin.setValue(0.0)
            self.softGroundSpin.setEnabled(False)
            self.softGroundSpin.setToolTip(
                "Hard ground is treated as 0% soft ground."
            )
        elif ground_type == GroundType.SOFT:
            self.softGroundSpin.setValue(100.0)
            self.softGroundSpin.setEnabled(False)
            self.softGroundSpin.setToolTip(
                "Soft ground is treated as 100% soft ground."
            )
        else:
            self.softGroundSpin.setEnabled(True)
            self.softGroundSpin.setToolTip(
                "Enter the proportion of the source-to-receptor path "
                "that is acoustically soft ground."
            )

    def _soft_ground_percent_for_source(
        self,
        ground_type: GroundType,
    ) -> float:
        """Return the effective soft-ground proportion for one source."""

        if ground_type == GroundType.HARD:
            return 0.0

        if ground_type == GroundType.SOFT:
            return 100.0

        return float(self.softGroundSpin.value())

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
                    f"No source features selected. All {source_layer.featureCount()} "
                    "source feature(s) will be calculated."
                )
            elif count == 1:
                feature = next(source_layer.getSelectedFeatures())
                self.sourceStatusLabel.setText(
                    f"1 source selected: {self._source_identifier(feature)}. "
                    "Only the selected source will be calculated."
                )
            else:
                self.sourceStatusLabel.setText(
                    f"{count} source features selected. "
                    "Only selected sources will be calculated."
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
        """Calculate selected sources, or all sources when none are selected."""

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

        selected_source_count = source_layer.selectedFeatureCount()
        if selected_source_count > 0:
            source_features = list(source_layer.getSelectedFeatures())
            source_scope = "selected"
        else:
            source_features = list(source_layer.getFeatures())
            source_scope = "all"

        if not source_features:
            QMessageBox.warning(
                self,
                "No sources",
                "The source point layer is empty.",
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
            self._prediction_records_by_receptor = {}
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
                            soft_ground_percent=(
                                self._soft_ground_percent_for_source(
                                    source.ground_type
                                )
                            ),
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
                            dominant_result, decimals=2
                        ),
                        "combined_level_db": combined_level,
                    }
                    prediction_records.append(record)
                    self._prediction_records_by_receptor[
                        int(receptor_feature.id())
                    ] = record
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

            self._show_statistical_summary(
                prediction_records,
                source_count=len(source_features),
            )
            self._show_receptor_details(first_record)
            self.distanceSpin.setValue(first_record["nearest_distance_m"])
            self.tabWidget.setCurrentWidget(self.resultsTab)

            scope_text = (
                "selected source(s)" if source_scope == "selected"
                else "all source(s)"
            )
            message = (
                f"Completed cumulative predictions from {len(source_features)} "
                f"{scope_text} for {len(prediction_records)} receptor(s)."
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
                QgsVectorFileWriter.ActionOnExistingFile.CreateOrOverwriteLayer
            )
        else:
            options.actionOnExistingFile = (
                QgsVectorFileWriter.ActionOnExistingFile.CreateOrOverwriteFile
            )

        result = QgsVectorFileWriter.writeAsVectorFormatV3(
            source_layer,
            output_path,
            QgsProject.instance().transformContext(),
            options,
        )
        error_code = result[0] if isinstance(result, tuple) else result
        if error_code != QgsVectorFileWriter.WriterError.NoError:
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
        options.actionOnExistingFile = QgsVectorFileWriter.ActionOnExistingFile.CreateOrOverwriteFile

        result = QgsVectorFileWriter.writeAsVectorFormatV3(
            source_layer,
            output_path,
            QgsProject.instance().transformContext(),
            options,
        )
        error_code = result[0] if isinstance(result, tuple) else result
        if error_code != QgsVectorFileWriter.WriterError.NoError:
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
        renderer.setMode(QgsGraduatedSymbolRenderer.Mode.Custom)
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
            f'{record["nearest_distance_m"]:.2f}',
            record["dominant_source_id"],
            f'{record["dominant_source_level_db"]:.2f}',
            f"{dominant_result.predicted_level_db:.2f}",
            f'{record["combined_level_db"]:.2f}',
        ]
        for column, value in enumerate(values):
            item = QTableWidgetItem(value)
            if column in (1, 2, 4, 5, 6):
                item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            item.setData(Qt.ItemDataRole.UserRole, receptor_feature.id())
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

        return item.data(Qt.ItemDataRole.UserRole)

    def _on_result_selection_changed(self) -> None:
        """Select the corresponding receptor and show its calculation details."""

        receptor_fid = self._selected_receptor_fid()
        if receptor_fid is None:
            return

        self._select_receptor_from_table(show_warning=False)
        record = self._prediction_records_by_receptor.get(int(receptor_fid))
        if record is not None:
            self._show_receptor_details(record)

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

    def _show_statistical_summary(
        self,
        prediction_records,
        source_count: int,
    ) -> None:
        """Show project-wide statistics for all successfully assessed receptors."""

        if not prediction_records:
            return

        levels = [
            float(record["combined_level_db"])
            for record in prediction_records
        ]
        highest_record = max(
            prediction_records,
            key=lambda record: float(record["combined_level_db"]),
        )
        highest_receptor = self._receptor_identifier(
            highest_record["receptor_feature"]
        )

        self.distanceResultLabel.setText(str(source_count))
        self.groundResultLabel.setText(str(len(prediction_records)))
        self.screeningResultLabel.setText(f"{min(levels):.2f} dB")
        self.reflectionResultLabel.setText(f"{max(levels):.2f} dB")
        self.durationResultLabel.setText(
            f"{sum(levels) / len(levels):.2f} dB"
        )
        self.beforeDurationResultLabel.setText(highest_receptor)
        self.predictedResultLabel.setText(f"{max(levels):.2f} dB")

    def _show_receptor_details(self, record) -> None:
        """Show the calculation breakdown for the selected receptor."""

        if record is None:
            return

        result = record["dominant_result"]
        receptor_id = self._receptor_identifier(record["receptor_feature"])

        self.detailReceptorLabel.setText(receptor_id)
        self.detailDistanceLabel.setText(
            f"−{result.distance_attenuation_db:.2f} dB"
        )
        ground_attenuation = (
            0.0
            if abs(result.ground_attenuation_db) < 0.005
            else result.ground_attenuation_db
        )
        self.detailGroundLabel.setText(
            f"−{ground_attenuation:.2f} dB"
            if ground_attenuation > 0
            else "0.00 dB"
        )
        screening_attenuation = (
            0.0
            if abs(result.screening_attenuation_db) < 0.005
            else result.screening_attenuation_db
        )
        self.detailScreeningLabel.setText(
            f"−{screening_attenuation:.2f} dB"
            if screening_attenuation > 0
            else "0.00 dB"
        )
        self.detailReflectionLabel.setText(
            f"+{result.reflection_correction_db:.2f} dB"
        )
        self.detailDurationLabel.setText(
            f"{result.duration_correction_db:+.2f} dB"
        )
        self.detailDominantLabel.setText(
            f'{record["dominant_source_id"]}: '
            f"{result.predicted_level_db:.2f} dB"
        )
        self.detailCombinedLabel.setText(
            f'{record["combined_level_db"]:.2f} dB'
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
            self.distanceResultLabel,
            self.groundResultLabel,
            self.screeningResultLabel,
            self.reflectionResultLabel,
            self.durationResultLabel,
            self.beforeDurationResultLabel,
            self.predictedResultLabel,
            self.detailReceptorLabel,
            self.detailDistanceLabel,
            self.detailGroundLabel,
            self.detailScreeningLabel,
            self.detailReflectionLabel,
            self.detailDurationLabel,
            self.detailDominantLabel,
            self.detailCombinedLabel,
        ):
            label.setText("—")
        self._prediction_records_by_receptor = {}
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
