import sys
import unittest

PLUGIN_PATH = r"D:\QGIS_Plugin_Development\Noise-Prediction-Algorithm"

if PLUGIN_PATH not in sys.path:
    sys.path.insert(0, PLUGIN_PATH)

suite = unittest.defaultTestLoader.loadTestsFromName(
    "tests.test_bs5228_engine"
)

runner = unittest.TextTestRunner(verbosity=2)
result = runner.run(suite)

if result.wasSuccessful():
    print("All BS 5228 engine tests passed.")
else:
    print("Some tests failed.")
