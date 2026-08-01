# 🔊 Noise Prediction
![QGIS](https://img.shields.io/badge/QGIS-3.x-green)
![Version](https://img.shields.io/badge/version-v0.5.0--beta-blue)
![License](https://img.shields.io/badge/license-GPL%20v2-orange)
![Status](https://img.shields.io/badge/status-Beta-yellow)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)

> **A QGIS plugin for predicting cumulative construction noise levels at receptor locations.**

<p align="center">
  <img src="docs/images/hero_screenshot.png" width="100%">
</p>

<p align="center">
<b>Experimental Beta • QGIS 3.x • Open Source • GPL License</b>
</p>

---

## Overview

**Noise Prediction** is an open-source QGIS plugin designed to estimate cumulative construction noise levels at receptor locations using a practical and easy-to-use workflow within the QGIS environment.

The plugin enables users to evaluate construction noise impacts from multiple noise sources while considering important influencing factors such as operating duration, ground conditions, screening attenuation, and reflection corrections. Results are automatically summarized in attribute tables and GIS layers for visualization, analysis, and reporting.

The project is intended for:

- 🌱 Environmental consultants
- 🏗 Construction planners
- 🗺 GIS professionals
- 🎓 Researchers and students
- 🏛 Government organizations
- 🌍 Environmental impact assessment (EIA) practitioners

The current release focuses on providing a transparent, practical, and user-friendly workflow that can be easily adapted for environmental assessment and educational purposes.

> **Important**
>
> This plugin uses a **simplified calculation workflow inspired by principles described in BS 5228**.
>
> It is **not an official implementation of BS 5228** and should **not** be considered a replacement for detailed acoustic modelling or regulatory noise assessment. Users are responsible for reviewing and validating prediction results before using them for engineering, contractual, or regulatory purposes.

---

# Key Features

✔ Predict cumulative noise from multiple construction sources

✔ Calculate noise levels at multiple receptor locations

✔ Support both **Shared Parameters** and **Source-Specific** calculation workflows

✔ Apply activity duration correction using assessment period

✔ Support Hard, Soft, and Mixed ground conditions

✔ Apply manual screening attenuation

✔ Apply manual reflection correction

✔ Automatic cumulative noise calculation

✔ Create GIS output layers

✔ Generate detailed prediction tables

✔ Include demonstration datasets for learning

✔ Designed for education, research, and preliminary environmental assessment

---

## Plugin Preview

The current beta version provides an intuitive graphical interface built with Qt Designer.

<p align="center">
<img src="docs/images/plugin_interface.png" width="95%">
</p>

The interface guides users through each step of the prediction workflow, from selecting input layers to configuring calculation parameters and generating prediction outputs.

---

# Installation

## System Requirements

Before installing the plugin, ensure your system meets the following requirements.

| Requirement | Version |
|-------------|---------|
| QGIS | 3.16 or later (Recommended: Latest QGIS 3 LTR) |
| Operating System | Windows, Linux, or macOS |
| Python | Included with QGIS |
| Additional Libraries | None |

> **Note**
>
> The current beta version has been developed and tested using **QGIS 3.x** with **PyQt5**.

---

## Option 1 – Install from ZIP (Recommended)

The easiest way to install the plugin is from the latest release package.

### Step 1

Download the latest plugin ZIP file from the **Releases** page.

**GitHub → Releases → Download `Noise_Prediction_v0.5.0_beta.zip`**

*(Replace this with the actual release link after publishing.)*

---

### Step 2

Open **QGIS**.

Navigate to

**Plugins → Manage and Install Plugins...**

<p align="center">
<img src="docs/images/install_plugin_manager.png" width="80%">
</p>

---

### Step 3

Select

**Install from ZIP**

Browse to the downloaded ZIP file and click **Install Plugin**.

<p align="center">
<img src="docs/images/install_zip.png" width="80%">
</p>

---

### Step 4

Once installation is complete, enable the plugin if it is not already activated.

The **Noise Prediction** button will appear in the QGIS toolbar.

<p align="center">
<img src="docs/images/plugin_toolbar.png" width="80%">
</p>

---

## Option 2 – Install from QGIS Plugin Repository

> **Coming Soon**

The plugin will be available through the official QGIS Plugin Repository after the beta testing phase.

Once published, installation will simply require searching for **"Noise Prediction"** in the QGIS Plugin Manager.

---

## Verify Installation

After successful installation:

- The plugin icon appears in the QGIS toolbar.
- The plugin is listed under **Plugins → Manage and Install Plugins**.
- Clicking the toolbar icon opens the Noise Prediction dialog.

<p align="center">
<img src="docs/images/plugin_loaded.png" width="90%">
</p>

---

## Troubleshooting

### The plugin does not appear

- Restart QGIS.
- Ensure the plugin is enabled.
- Confirm you installed the correct ZIP package.

---

### Installation fails

- Verify you are using a supported version of QGIS.
- Download the latest release again.
- Remove any older versions of the plugin before reinstalling.

---

### Unexpected errors

If you encounter an issue, please submit a bug report on the project's **GitHub Issues** page.

When reporting a problem, include:

- Operating system
- QGIS version
- Plugin version
- Steps to reproduce the issue
- Error message or screenshot (if available)

This information helps identify and resolve issues more efficiently.

---

# Quick Start - Your First Noise Prediction

This guide demonstrates the basic workflow for generating your first construction noise prediction using the sample datasets included with the plugin.

> **Estimated Time:** 5–10 minutes

---

## Step 1 – Open QGIS

Launch **QGIS** and create a new project.

It is recommended to save the project before starting the analysis.

<p align="center">
<img src="docs/images/qgis_project.png" width="90%">
</p>

---

## Step 2 – Load the Sample Data

The plugin includes demonstration datasets located in:

```text
dataset/sample_data_v0.5.0 beta/
```

Load the following layers into QGIS:

- Construction Sources
- Receptors

Both layers should appear in the **Layers Panel**.

<p align="center">
<img src="docs/images/sample_layers.png" width="90%">
</p>

---

## Step 3 – Open the Plugin

Click the **Noise Prediction** button in the QGIS toolbar.

Alternatively, open the plugin from:

**Plugins → Noise Prediction**

<p align="center">
<img src="docs/images/open_plugin.png" width="90%">
</p>

---

## Step 4 – Select Input Layers

Choose:

| Setting | Layer |
|---------|-------|
| Source Layer | Construction Sources |
| Receptor Layer | Receptors |

The plugin will automatically verify that both layers are valid point layers.

<p align="center">
<img src="docs/images/select_layers.png" width="90%">
</p>

---

## Step 5 – Configure Prediction Parameters

Select the prediction method that best matches your data.

### Option A – Shared Parameters

Use the same parameter values for every construction source.

Recommended for:

- Small projects
- Quick assessments
- Educational demonstrations

---

### Option B – Source-Specific Parameters

Read parameter values directly from the source layer attributes.

Recommended for:

- Real construction projects
- Multiple equipment types
- Different operating conditions

<p align="center">
<img src="docs/images/source_specific.png" width="90%">
</p>

---

## Step 6 – Run the Prediction

Click **Run Prediction**.

The plugin will automatically:

- Validate the input layers
- Calculate noise propagation
- Apply selected corrections
- Predict cumulative noise levels
- Create output layers
- Generate a results table

Depending on the number of sources and receptors, processing may take a few seconds.

---

## Step 7 – Review the Results

When the calculation is complete, the plugin produces:

- Predicted receptor noise levels
- Total cumulative noise values
- Detailed calculation table
- GIS output layer
- Processing summary

<p align="center">
<img src="docs/images/results_table.png" width="90%">
</p>

---

## Step 8 – Visualize the Output

The resulting layer can be symbolized using graduated colours to identify areas with different predicted noise levels.

Example:

🟢 Low Noise

🟡 Moderate Noise

🟠 High Noise

🔴 Very High Noise

<p align="center">
<img src="docs/images/output_map.png" width="90%">
</p>

---

## Congratulations!

You have successfully completed your first construction noise prediction.

The following sections explain each plugin option, required input data, calculation methodology, and output fields in greater detail.

👉 Continue to the **Plugin Interface Guide** for a detailed explanation of every control and parameter.

---

# 📚 Documentation

The documentation is organized into a series of guides to help users understand every aspect of the plugin, from installation to interpreting prediction results.

Whether you are a first-time user or an experienced GIS professional, the following guides provide step-by-step instructions, practical examples, and technical explanations.

| Guide | Description |
|--------|-------------|
| 📦 [Installation Guide](docs/installation.md) | Install the plugin and verify a successful installation. |
| 🚀 [Quick Start Guide](docs/getting_started.md) | Complete your first construction noise prediction in just a few minutes. |
| 🖥 [Plugin Interface](docs/plugin_interface.md) | Learn the purpose of every control, parameter, and option available in the plugin. |
| 🔄 [Prediction Workflow](docs/workflow.md) | Follow the recommended workflow from input data preparation to final output generation. |
| 📂 [Input Data Guide](docs/input_data.md) | Understand the required layer structure, attributes, supported geometries, and data formats. |
| 🧮 [Calculation Methodology](docs/methodology.md) | Learn how the plugin estimates construction noise and applies distance, duration, ground, screening, and reflection corrections. |
| 📊 [Output Results](docs/outputs.md) | Understand the generated GIS layers, prediction tables, and output fields. |
| 📖 [Worked Example](docs/examples.md) | Reproduce a complete noise prediction using the included sample datasets. |
| ❓ [Frequently Asked Questions (FAQ)](docs/faq.md) | Find answers to common questions, troubleshooting tips, and known issues. |
| ⚠ [Limitations](docs/limitations.md) | Review the current capabilities, assumptions, and limitations of the beta version. |

---

## Need Help?

If you encounter an issue or have a question that is not covered in the documentation, you can:

- 🐞 Report bugs or request features through the GitHub **Issues** page.
- 💡 Suggest improvements to the documentation.
- ⭐ Support the project by starring the repository and sharing feedback.

Your feedback is valuable and helps improve future releases of the plugin.

## 📖 Documentation Roadmap

The documentation is organized in the recommended reading order for new users.

```text
Installation
      ↓
Quick Start
      ↓
Plugin Interface
      ↓
Prediction Workflow
      ↓
Input Data Guide
      ↓
Calculation Methodology
      ↓
Output Results
      ↓
Worked Example
      ↓
FAQ
```

Following this sequence will help you become familiar with the plugin before using it in real projects.

---

# 📂 Sample Data

To help users become familiar with the plugin, a demonstration dataset is included with this repository. The sample data allows you to complete a full construction noise prediction workflow without preparing your own GIS data.

The datasets are intended for learning, testing, and demonstrating the plugin's functionality.

> **Location**
>
> ```
> dataset/sample_data_v0.5.0 beta/
> ```

---

## Included Datasets

The sample package contains the following files:

| Dataset | Geometry | Description |
|----------|----------|-------------|
| **Construction Sources** | Point | Sample construction equipment or activity locations used as noise sources. |
| **Receptors** | Point | Sample receptor locations where predicted noise levels are calculated. |
| **README** | Document | Brief description of the sample datasets and recommended workflow. |

---

## Sample Workflow

The demonstration data can be used to complete a basic prediction in just a few minutes.

```text
Load Sample Layers
        ↓
Open Noise Prediction
        ↓
Select Source Layer
        ↓
Select Receptor Layer
        ↓
Configure Parameters
        ↓
Run Prediction
        ↓
Review Results
```

For a detailed walkthrough, refer to the **Quick Start Guide**.

---

## Coordinate Reference System (CRS)

The sample datasets are supplied with an appropriate projected Coordinate Reference System (CRS) for demonstration purposes.

If you use your own datasets, ensure that both the **Source** and **Receptor** layers use the same projected CRS before running the prediction. Using geographic coordinate systems (latitude/longitude) may produce incorrect distance calculations.

---

## Using Your Own Data

Once you are familiar with the sample data, you can replace it with your own project data.

Your input layers should meet the following basic requirements:

- Point geometry for construction sources
- Point geometry for receptor locations
- Valid projected CRS
- Required attribute fields (depending on the selected workflow)

Detailed data preparation instructions are available in the **Input Data Guide**.

---

## Data Disclaimer

The sample datasets are provided solely for demonstration and educational purposes.

They do **not** represent actual construction projects or environmental assessments and should **not** be used for engineering design, regulatory submissions, or official decision-making.

---

## 📸 Sample Dataset Preview

<p align="center">
<img src="docs/images/sample_data_preview.png" width="90%">
</p>

*Example view of the included construction source and receptor layers loaded in QGIS.*
> **Tip**
>
> After completing the example with the provided datasets, try replacing the sample layers with your own construction source and receptor data. This is the fastest way to become familiar with the plugin and understand how different input parameters influence the prediction results.

---

# 📸 Screenshots

The following screenshots provide an overview of the Noise Prediction plugin and demonstrate the complete workflow, from loading input data to reviewing prediction results.

These images are intended to help new users quickly understand the plugin interface and available functionality before performing their own analysis.

---

## Main Plugin Interface

The main dialog provides access to all prediction settings, including input layers, calculation parameters, ground conditions, duration correction, and output options.

<p align="center">
<img src="docs/images/plugin_interface.png" width="95%">
</p>

---

## Source-Specific Parameter Mapping

The plugin supports reading prediction parameters directly from source layer attributes. This allows each construction source to have its own noise level, operating duration, ground condition, screening attenuation, and reflection correction.

<p align="center">
<img src="docs/images/source_specific_mapping.png" width="95%">
</p>

---

## Shared Parameter Workflow

For quick assessments and educational demonstrations, the same parameter values can be applied to all construction sources.

<p align="center">
<img src="docs/images/shared_parameters.png" width="95%">
</p>

---

## Sample Input Data

Example construction source and receptor layers included with the plugin.

<p align="center">
<img src="docs/images/sample_data.png" width="95%">
</p>

---

## Prediction Results

After the prediction is completed, the plugin generates cumulative noise levels for every receptor and displays the results in an easy-to-read table.

<p align="center">
<img src="docs/images/results_table.png" width="95%">
</p>

---

## GIS Output Layer

Predicted receptor noise levels can be visualized directly in QGIS using graduated colours, making it easier to identify areas with higher predicted construction noise.

<p align="center">
<img src="docs/images/output_map.png" width="95%">
</p>

---

## Processing Summary

The plugin reports the number of processed sources and receptors, completed calculations, and output layer creation.

<p align="center">
<img src="docs/images/processing_summary.png" width="95%">
</p>

---

## Additional Examples

More examples and detailed workflows are available in the **Documentation** section.

Future releases will include additional screenshots covering advanced workflows, interpretation examples, and complete case studies.

---

# ⚠️ Important Notice & Current Limitations

The **Noise Prediction** plugin is currently released as an **experimental beta version (v0.5.0 Beta)**. It is intended to provide a practical and transparent workflow for estimating construction noise levels within the QGIS environment.

The plugin has been developed primarily for **education, research, preliminary environmental assessment, and decision support**. While every effort has been made to implement a logical and reliable workflow, users should understand the scope and assumptions of the current release.

---

## Intended Applications

The plugin is suitable for:

- Environmental impact assessment (EIA) screening
- Construction planning and preliminary noise evaluation
- Academic research and teaching
- GIS-based environmental analysis
- Training and demonstration purposes
- Community and stakeholder engagement

---

## Current Calculation Approach

The prediction workflow considers several key factors that influence construction noise propagation, including:

- Distance attenuation
- Activity duration correction
- Hard, soft, and mixed ground conditions
- Screening attenuation
- Reflection correction
- Cumulative noise from multiple construction sources

The methodology is designed to provide a practical estimation workflow that can be easily understood and applied within QGIS.

---

## Current Limitations

The current beta version does **not** include several advanced acoustic modelling features commonly found in specialised commercial software.

The following capabilities are **not currently supported**:

- Three-dimensional (3D) terrain modelling
- Building diffraction and complex barrier analysis
- Frequency-dependent (octave-band) calculations
- Meteorological corrections (e.g., wind and atmospheric conditions)
- Ground absorption modelling based on detailed acoustic parameters
- Dynamic or moving noise sources
- Line and area noise source modelling
- Automatic reflection modelling from surrounding structures
- Time-varying construction schedules
- Regulatory compliance verification

These features may be considered for future releases based on project development priorities and community feedback.

---

## BS 5228 Statement

The current calculation workflow is **inspired by engineering principles described in BS 5228** for construction noise assessment.

However:

- This plugin is **not an official implementation of BS 5228**.
- It does **not reproduce every procedure or calculation described in the standard**.
- The results should be considered **preliminary estimates** rather than certified engineering calculations.

Users requiring assessments for regulatory approval or legal compliance should refer to the complete BS 5228 standard and other applicable national or local guidance.

---

## Validation Responsibility

Users are responsible for reviewing the prediction results and determining whether the chosen assumptions and input parameters are appropriate for their project.

Predicted noise levels should be interpreted together with:

- Field measurements (where available)
- Project-specific construction information
- Professional engineering judgement
- Applicable environmental regulations and standards

---

## Beta Release

As an experimental release, the plugin is expected to evolve through community feedback.

You may encounter:

- Minor bugs
- User interface improvements
- Additional features in future versions
- Changes to workflows or calculation options

Bug reports, feature requests, and suggestions are welcome through the project's GitHub repository.

---

## Disclaimer

This software is provided **"as is"**, without warranty of any kind, express or implied.

The author and contributors accept no responsibility for any loss, damage, or consequences resulting from the use or interpretation of the prediction results.

Users are solely responsible for verifying the suitability of the software and its outputs for their intended application.

---

# 📄 License

This project is licensed under the **GNU General Public License v2.0 or later (GPL-2.0-or-later)**.

You are free to:

- ✔ Use the plugin for personal, academic, and commercial purposes.
- ✔ Study and modify the source code.
- ✔ Distribute copies of the original or modified software.
- ✔ Contribute improvements through pull requests.

Any redistributed or modified versions must comply with the terms of the GPL license.

For full license details, see the [LICENSE](LICENSE) file included in this repository.

---