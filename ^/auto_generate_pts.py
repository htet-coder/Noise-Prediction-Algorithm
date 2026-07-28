from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsFeature,
    QgsGeometry,
    QgsPointXY,
    QgsField,
)
from qgis.PyQt.QtCore import QVariant


project = QgsProject.instance()

# --------------------------------------------------
# Remove old test layers if they already exist
# --------------------------------------------------

for layer_name in [
    "TEST_Noise_Source",
    "TEST_Noise_Receptors",
]:
    for layer in project.mapLayersByName(layer_name):
        project.removeMapLayer(layer.id())


# --------------------------------------------------
# Create source point layer
# --------------------------------------------------

source_layer = QgsVectorLayer(
    "Point?crs=EPSG:32647",
    "TEST_Noise_Source",
    "memory",
)

source_provider = source_layer.dataProvider()

source_provider.addAttributes(
    [
        QgsField("source_id", QVariant.String),
        QgsField("source_db", QVariant.Double),
    ]
)

source_layer.updateFields()

source_feature = QgsFeature(source_layer.fields())

source_feature.setGeometry(
    QgsGeometry.fromPointXY(
        QgsPointXY(
            500000.0,
            2050000.0,
        )
    )
)

source_feature["source_id"] = "S01"
source_feature["source_db"] = 90.0

source_provider.addFeature(source_feature)

source_layer.updateExtents()

project.addMapLayer(source_layer)


# --------------------------------------------------
# Create receptor point layer
# --------------------------------------------------

receptor_layer = QgsVectorLayer(
    "Point?crs=EPSG:32647",
    "TEST_Noise_Receptors",
    "memory",
)

receptor_provider = receptor_layer.dataProvider()

receptor_provider.addAttributes(
    [
        QgsField("receptor_id", QVariant.String),
        QgsField("expected_m", QVariant.Double),
    ]
)

receptor_layer.updateFields()


receptor_data = [
    ("R01", 500010.0, 2050000.0, 10.0),
    ("R02", 500050.0, 2050000.0, 50.0),
    ("R03", 500100.0, 2050000.0, 100.0),
    ("R04", 500500.0, 2050000.0, 500.0),
]

features = []

for receptor_id, x, y, expected_distance in receptor_data:

    feature = QgsFeature(
        receptor_layer.fields()
    )

    feature.setGeometry(
        QgsGeometry.fromPointXY(
            QgsPointXY(x, y)
        )
    )

    feature["receptor_id"] = receptor_id
    feature["expected_m"] = expected_distance

    features.append(feature)


receptor_provider.addFeatures(features)

receptor_layer.updateExtents()

project.addMapLayer(receptor_layer)


# --------------------------------------------------
# Select the source feature
# --------------------------------------------------

source_layer.selectAll()


# --------------------------------------------------
# Zoom to sample data
# --------------------------------------------------

iface.mapCanvas().setExtent(
    receptor_layer.extent()
)

iface.mapCanvas().refresh()


print("Sample noise source and receptor layers created.")
print("Source S01 is already selected.")
print("Receptor distances: 10 m, 50 m, 100 m, 500 m.")
