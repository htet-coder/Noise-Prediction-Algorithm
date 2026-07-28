# -*- coding: utf-8 -*-

import importlib
import sys

PLUGIN_PATH = r"D:\QGIS_Plugin_Development\Noise-Prediction-Algorithm"

if PLUGIN_PATH not in sys.path:
    sys.path.insert(0, PLUGIN_PATH)

import core.bs5228_engine

engine = importlib.reload(core.bs5228_engine)

data = engine.PredictionInput(
    source_level_db=90.0,
    distance_m=100.0,
    ground_type=engine.GroundType.HARD,
    screening_type=engine.ScreeningType.FULL,
    reflection_correction_db=3.0,
    activity_duration_hours=4.0,
    assessment_duration_hours=8.0,
)

result = engine.predict_noise_level(data)
result = engine.round_result(result)

print("=" * 50)
print("BS 5228 DEVELOPMENT TEST")
print("=" * 50)
print(f"Source level:          {result.source_level_db} dB")
print(f"Distance:              {result.distance_m} m")
print(f"Distance attenuation:  {result.distance_attenuation_db} dB")
print(f"Ground attenuation:    {result.ground_attenuation_db} dB")
print(f"Screen attenuation:    {result.screening_attenuation_db} dB")
print(f"Reflection correction: {result.reflection_correction_db} dB")
print(f"Duration correction:   {result.duration_correction_db} dB")
print("-" * 50)
print(f"Predicted level:        {result.predicted_level_db} dB")
print("=" * 50)