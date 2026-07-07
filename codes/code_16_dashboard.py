"""
code_16_dashboard.py — Streamlit Polymer Inverse Design Dashboard.

Imports BACKBONES, LEFT_GROUPS, RIGHT_GROUPS from constants.py (single source
of truth). Uses a seeded np.random.Generator for deterministic candidate
generation on every button click.
"""
from __future__ import annotations

import sys
from io import BytesIO
from pathlib import Path

import base64
import joblib
import numpy as np
import pandas as pd
import streamlit as st
from rdkit import Chem
from rdkit.Chem import Draw, rdMolDescriptors

# ── Shared polymer library ────────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).resolve().parent))
from constants import BACKBONES, LEFT_GROUPS, RIGHT_GROUPS  # noqa: E402

# ── Paths ─────────────────────────────────────────────────────────────────────
_REPO_ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH: Path = _REPO_ROOT / "files" / "ansys_ensemble_pipeline.pkl"

# ── UI Configuration ──────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Polymer Inverse Design",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stButton>button {width: 100%; border-radius: 5px; height: 3em; background-color: #ff4b4b; color: white;}
    </style>
    """,
    unsafe_allow_html=True,
)


# ── Helpers ───────────────────────────────────────────────────────────────────
@st.cache_resource
def load_model():
    if MODEL_PATH.exists():
        return joblib.load(MODEL_PATH)
    return None


def smiles_to_morgan(smi: str, n_bits: int = 512) -> np.ndarray:
    mol = Chem.MolFromSmiles(smi)
    if mol is None:
        return np.zeros(n_bits)
    fp = rdMolDescriptors.GetMorganFingerprintAsBitVect(mol, radius=2, nBits=n_bits)
    return np.array(fp)


def render_molecule(smi: str):
    mol = Chem.MolFromSmiles(smi)
    if mol:
        return Draw.MolToImage(mol, size=(250, 100), kekulize=True)
    return None


# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.title("⚡ Settings")
st.sidebar.markdown("Configure the Inverse Design constraints:")

target_cap = st.sidebar.number_input(
    "Target Capacitance (pF/m)", min_value=10.0, max_value=2000.0, value=200.0, step=10.0
)
library_size = st.sidebar.slider(
    "Virtual Library Size",
    min_value=1000, max_value=25000, value=10000, step=1000,
    help="Larger libraries take longer but find better matches.",
)
thickness_range = st.sidebar.slider(
    "Thickness Constraint (nm)", min_value=100, max_value=5000, value=(500, 3000), step=100
)

st.sidebar.markdown("---")
st.sidebar.markdown("**Powered by:** ANSYS Maxwell 2D & XGBoost")

# ── Main Page ─────────────────────────────────────────────────────────────────
st.title("🔬 Polymer Informatics Inverse Design")
st.markdown(
    "Enter a target capacitance and the Physics-Informed ML Ensemble will "
    "recommend the exact polymer structure and manufacturing parameters to achieve it."
)

model = load_model()

if model is None:
    st.error(f"Model `{MODEL_PATH}` not found. Please wait for your training script to finish.")
else:
    if st.button("🚀 Run AI Inverse Design Discovery"):
        with st.spinner(f"Generating and screening {library_size:,} candidates..."):
            # Use a seeded rng for deterministic generation — same button press → same results
            rng = np.random.default_rng(42)
            backbone_names = list(BACKBONES.keys())

            candidates: list[dict] = []
            fps: list[np.ndarray] = []

            for _ in range(library_size):
                name = backbone_names[int(rng.integers(len(backbone_names)))]
                meta = BACKBONES[name]
                lg = LEFT_GROUPS[int(rng.integers(len(LEFT_GROUPS)))]
                rg = RIGHT_GROUPS[int(rng.integers(len(RIGHT_GROUPS)))]
                smi = f"{lg}{meta['backbone']}{rg}"

                thick = rng.uniform(thickness_range[0], thickness_range[1])
                volt = rng.uniform(10, 500)

                candidates.append({
                    "smiles": smi,
                    "base_material": name,
                    "dielectric_constant": meta["eps"] + rng.uniform(-0.1, 0.1),
                    "tg_celsius": meta["tg"] + rng.uniform(-5, 5),
                    "density_g_cm3": meta["density"] + rng.uniform(-0.05, 0.05),
                    "thickness_nm": thick,
                    "applied_voltage": volt,
                    "temp_c": 25,
                })
                fps.append(smiles_to_morgan(smi))

            df_cand = pd.DataFrame(candidates)
            fp_cols = [f"Morgan_{i}" for i in range(512)]
            df_fps = pd.DataFrame(np.vstack(fps), columns=fp_cols)
            physical_cols = [
                "dielectric_constant", "tg_celsius", "density_g_cm3",
                "thickness_nm", "applied_voltage", "temp_c",
            ]

            X = pd.concat([df_fps, df_cand[physical_cols]], axis=1)
            preds = model.predict(X)

            df_cand["predicted_capacitance"] = preds
            df_cand["error"] = abs(df_cand["predicted_capacitance"] - target_cap)

            ranked = df_cand.sort_values(by="error").head(6).reset_index(drop=True)

            st.success(
                f"Screening Complete! Maximum deviation from target: {ranked['error'].iloc[0]:.3f} pF/m"
            )

            cols = st.columns(3)
            for i, row in ranked.iterrows():
                col = cols[i % 3]
                with col:
                    st.markdown(f"### Rank #{i+1}")
                    st.markdown(f"**Predicted:** `{row['predicted_capacitance']:.2f} pF/m`")
                    st.markdown(f"**Base:** {row['base_material']}")
                    st.markdown(f"**Thickness:** {row['thickness_nm']:.1f} nm")

                    img = render_molecule(row["smiles"])
                    if img:
                        st.image(img, use_container_width=True)
                    st.caption(f"SMILES: `{row['smiles']}`")
                    st.markdown("---")
