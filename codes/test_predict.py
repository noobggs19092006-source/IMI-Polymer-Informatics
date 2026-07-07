import pickle
import pandas as pd
import numpy as np

with open("../files/ansys_ensemble_pipeline.pkl", "rb") as f:
    m = pickle.load(f)

df = pd.DataFrame(
    np.zeros((1, 518)),
    columns=[f"morgan_{i}" for i in range(512)]
    + [
        "dielectric_constant",
        "tg_celsius",
        "density_g_cm3",
        "thickness_nm",
        "applied_voltage",
        "temp_c",
    ],
)
print("Predicting with DataFrame...")
try:
    print(m.predict(df))
except Exception as e:
    import traceback

    traceback.print_exc()

print("Predicting with Numpy Array...")
try:
    print(m.predict(df.values))
except Exception as e:
    import traceback

    traceback.print_exc()
