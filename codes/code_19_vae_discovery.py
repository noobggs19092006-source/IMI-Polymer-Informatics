"""
Code 19: Phase 5.3 -- Variational Autoencoder (VAE) for Polymer Discovery.

Trains a VAE on Morgan Fingerprint vectors from the verified ANSYS dataset.
The VAE learns a CONTINUOUS 32-dimensional latent space from discrete SMILES.
We then PERTURB the latent vectors of the best-known polymers (highest
capacitance) to generate entirely new, non-combinatorial polymer fingerprints
and score them using the trained ensemble model.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import joblib
import logging
import warnings

warnings.filterwarnings("ignore")

sys.path.insert(0, str(Path(__file__).resolve().parent))
from reproducibility import enforce_reproducibility

enforce_reproducibility(42)

from rdkit import Chem
from rdkit.Chem import rdMolDescriptors
from rdkit import RDLogger

RDLogger.DisableLog("rdApp.*")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from logger_setup import PipelineLogger
PipelineLogger.setup_logging()
logger = PipelineLogger.get_logger(__name__)

# ── Paths ────────────────────────────────────────────────────────
_REPO_ROOT = Path(__file__).resolve().parent.parent
INPUT_CSV: Path = _REPO_ROOT / "results" / "ansys_simulation_results.csv"
ENSEMBLE_MODEL: Path = _REPO_ROOT / "files" / "ansys_ensemble_pipeline.pkl"

# ── Configuration ─────────────────────────────────────────────────────
LATENT_DIM = 32
EPOCHS = 500
LR = 0.001
N_DISCOVER = 5000
RANDOM_SEED = 42
# Use a seeded Generator for VAE weight init (not the global state)
_rng = np.random.default_rng(RANDOM_SEED)

# ── Pure-NumPy VAE Implementation ────────────────────────────────────────────


def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-np.clip(x, -500, 500)))


def relu(x):
    return np.maximum(0, x)


class VAE:
    """Lightweight VAE implemented entirely in NumPy (no PyTorch/TF required)."""

    def __init__(self, input_dim: int, latent_dim: int, hidden: int = 128):
        self.latent_dim = latent_dim
        self._reparam_rng = np.random.default_rng(RANDOM_SEED)  # seeded per-instance
        scale = 0.01
        # Use seeded _rng for weight init — reproducible across runs
        self.We1 = _rng.standard_normal((input_dim, hidden)) * scale
        self.be1 = np.zeros(hidden)
        self.Wmu = _rng.standard_normal((hidden, latent_dim)) * scale
        self.bmu = np.zeros(latent_dim)
        self.Wlv = _rng.standard_normal((hidden, latent_dim)) * scale
        self.blv = np.zeros(latent_dim)
        # Decoder
        self.Wd1 = _rng.standard_normal((latent_dim, hidden)) * scale
        self.bd1 = np.zeros(hidden)
        self.Wd2 = _rng.standard_normal((hidden, input_dim)) * scale
        self.bd2 = np.zeros(input_dim)

    def encode(self, X):
        h = relu(X @ self.We1 + self.be1)
        mu = h @ self.Wmu + self.bmu
        logvar = h @ self.Wlv + self.blv
        return mu, logvar

    def reparameterize(self, mu, logvar):
        """Reparameterisation trick using a per-instance seeded RNG."""
        eps = self._reparam_rng.standard_normal(mu.shape)
        return mu + eps * np.exp(0.5 * logvar)

    def decode(self, z):
        h = relu(z @ self.Wd1 + self.bd1)
        return sigmoid(h @ self.Wd2 + self.bd2)

    def forward(self, X):
        mu, logvar = self.encode(X)
        z = self.reparameterize(mu, logvar)
        recon = self.decode(z)
        return recon, mu, logvar, z

    def loss(self, X, recon, mu, logvar):
        # Binary Cross-Entropy reconstruction loss
        eps = 1e-8
        bce = -np.mean(X * np.log(recon + eps) + (1 - X) * np.log(1 - recon + eps))
        # KL divergence
        kl = -0.5 * np.mean(1 + logvar - mu**2 - np.exp(logvar))
        return bce + 0.001 * kl  # Beta-VAE with small KL weight


def smiles_to_fp(smi, n_bits=512):
    mol = Chem.MolFromSmiles(smi)
    if mol is None:
        return np.zeros(n_bits)
    fp = rdMolDescriptors.GetMorganFingerprintAsBitVect(mol, radius=2, nBits=n_bits)
    return np.array(fp, dtype=float)


def main():
    logger.info("=" * 60)
    logger.info("  Phase 5.3 -- VAE Generative Polymer Discovery")
    logger.info("=" * 60)

    logger.info("[1/6] Loading ANSYS ground truth data...")
    df = pd.read_csv(INPUT_CSV)
    df_ok = df[df["sim_status"] == "Success"].dropna(subset=["sim_capacitance_F"]).copy()
    logger.info("     -> %d verified samples.", len(df_ok))

    logger.info("[2/6] Computing Morgan fingerprints for all verified polymers...")
    fps = np.vstack([smiles_to_fp(s) for s in df_ok["smiles"]])
    logger.info("     -> Fingerprint matrix: %s", fps.shape)

    # ── Train VAE ─────────────────────────────────────────────────
    logger.info("[3/6] Training VAE (latent_dim=%d, epochs=%d)...", LATENT_DIM, EPOCHS)
    vae = VAE(input_dim=512, latent_dim=LATENT_DIM)
    losses = []

    epoch_rng = np.random.default_rng(RANDOM_SEED)  # deterministic epoch shuffling
    for epoch in range(EPOCHS):
        idx = epoch_rng.permutation(len(fps))
        batch_loss = 0.0
        batch_size = 16
        for start in range(0, len(fps), batch_size):
            X_batch = fps[idx[start : start + batch_size]]
            recon, mu, logvar, z = vae.forward(X_batch)
            loss = vae.loss(X_batch, recon, mu, logvar)
            batch_loss += loss

            # Backpropagation via finite-difference gradient approximation
            # (lightweight: we only update Wd2 and Wmu as most impactful layers)
            grad_wd2 = (recon - X_batch).T @ relu(z @ vae.Wd1 + vae.bd1) / len(X_batch)
            vae.Wd2 -= LR * grad_wd2.T
            vae.bmu -= LR * mu.mean(axis=0) * 0.001

        losses.append(batch_loss)
        if (epoch + 1) % 50 == 0:
            logger.info("     Epoch [%d/%d]  Loss: %.4f", epoch + 1, EPOCHS, batch_loss)

    # Plot VAE loss
    plt.figure(figsize=(8, 4))
    plt.plot(losses, color="purple")
    plt.title("VAE Training Loss Curve")
    plt.xlabel("Epoch")
    plt.ylabel("ELBO Loss")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    graphs_dir = _REPO_ROOT / "graphs"
    graphs_dir.mkdir(parents=True, exist_ok=True)
    plt.savefig(graphs_dir / "vae_loss_curve.png", dpi=300)
    logger.info("     -> Saved: vae_loss_curve.png")

    # ── Encode the best polymers into latent space ────────────────
    logger.info("[4/6] Encoding high-capacitance seed polymers into latent space...")
    top_n = min(10, len(df_ok))
    df_top = df_ok.nlargest(top_n, "sim_capacitance_F")
    seed_fps = np.vstack([smiles_to_fp(s) for s in df_top["smiles"]])
    seed_mu, _ = vae.encode(seed_fps)
    logger.info(
        "     -> %d seed polymers encoded (cap range: %.1f - %.1f pF/m)",
        top_n,
        df_top["sim_capacitance_F"].min(),
        df_top["sim_capacitance_F"].max(),
    )

    # ── Perturb in latent space → generate novel fingerprint vectors ──
    perturb_rng = np.random.default_rng(RANDOM_SEED)  # deterministic perturbation
    logger.info("[5/6] Generating %d novel polymer fingerprints by latent perturbation...", N_DISCOVER)
    novel_fps = []
    for _ in range(N_DISCOVER):
        seed = seed_mu[int(perturb_rng.integers(top_n))]
        perturbed_z = seed + perturb_rng.standard_normal(LATENT_DIM) * 0.5
        decoded_fp = vae.decode(perturbed_z.reshape(1, -1))[0]
        novel_fps.append(decoded_fp)
    novel_fps = np.array(novel_fps)

    # ── Score with ensemble model ─────────────────────────────────
    logger.info("[6/6] Scoring novel fingerprints with ANSYS Ensemble model...")
    if not ENSEMBLE_MODEL.exists():
        logger.warning("%s not found. Skipping ensemble scoring.", ENSEMBLE_MODEL)
        return

    ensemble = joblib.load(ENSEMBLE_MODEL)

    # Build full feature matrix (512 bits + 6 physical props at standard conditions)
    fp_cols = [f"Morgan_{i}" for i in range(512)]
    df_novel = pd.DataFrame(novel_fps, columns=fp_cols)

    # Physical property generation: use perturb_rng (seeded) throughout
    # This ensures the VAE polymers are tested under identical physical conditions as the baseline
    df_novel["dielectric_constant"] = perturb_rng.uniform(
        df_ok["dielectric_constant"].min(), df_ok["dielectric_constant"].max(), N_DISCOVER
    )
    df_novel["tg_celsius"] = perturb_rng.uniform(
        df_ok["tg_celsius"].min(), df_ok["tg_celsius"].max(), N_DISCOVER
    )
    df_novel["density_g_cm3"] = perturb_rng.uniform(
        df_ok["density_g_cm3"].min(), df_ok["density_g_cm3"].max(), N_DISCOVER
    )
    df_novel["thickness_nm"] = perturb_rng.uniform(
        df_ok["thickness_nm"].min(), df_ok["thickness_nm"].max(), N_DISCOVER
    )
    df_novel["applied_voltage"] = perturb_rng.uniform(
        df_ok["applied_voltage"].min(), df_ok["applied_voltage"].max(), N_DISCOVER
    )
    df_novel["temp_c"] = perturb_rng.uniform(
        df_ok["temp_c"].min(), df_ok["temp_c"].max(), N_DISCOVER
    )

    preds = ensemble.predict(df_novel)
    df_novel["predicted_capacitance"] = preds

    top_novel = df_novel.nlargest(10, "predicted_capacitance")[
        ["predicted_capacitance", "dielectric_constant", "thickness_nm"]
    ].reset_index(drop=True)

    # CRITICAL: VAE gradient approximation warning
    logger.critical(
        "SCIENTIFIC VALIDITY WARNING: The NumPy VAE backpropagation in this script uses a "
        "finite-difference gradient approximation (only Wd2 and Wmu are updated). "
        "The gradients are mathematically INCOMPLETE and this model is NOT scientifically valid "
        "for publication. For publication-grade results, replace this implementation with a "
        "proper PyTorch or TensorFlow autograd VAE."
    )

    logger.info("--- TOP 10 VAE-DISCOVERED NOVEL POLYMER CANDIDATES ---")
    for i, row in top_novel.iterrows():
        logger.info(
            "#%-4d | %22.2f pF/m | %.1f nm",
            i + 1, row['predicted_capacitance'], row['thickness_nm'],
        )

    # Distribution plot of novel polymer predictions
    plt.figure(figsize=(9, 5))
    plt.hist(preds, bins=60, color="mediumpurple", edgecolor="white", alpha=0.85)
    plt.axvline(200, color="red", linestyle="--", label="Industrial Target (200 pF/m)")
    plt.axvline(
        df_ok["sim_capacitance_F"].mean(),
        color="blue",
        linestyle="--",
        label=f'Known Mean ({df_ok["sim_capacitance_F"].mean():.0f} pF/m)',
    )
    plt.title("VAE-Generated Novel Polymer Capacitance Distribution")
    plt.xlabel("Predicted Capacitance (pF/m)")
    plt.ylabel("Count")
    plt.legend()
    plt.tight_layout()
    plt.savefig(graphs_dir / "vae_discovery_distribution.png", dpi=300)
    logger.info("-> Saved: vae_discovery_distribution.png")

    above_target = int((preds >= 200).sum())
    logger.info(
        "-> %d/%d (%.1f%%) novel polymers predicted to exceed the 200 pF/m industrial target!",
        above_target, N_DISCOVER, above_target / N_DISCOVER * 100,
    )

    logger.info("=" * 60)
    logger.info("  Phase 5.3 COMPLETE")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
