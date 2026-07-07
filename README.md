# Physics-Informed Polymer Informatics & Digital Twin Pipeline

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Enabled-blue.svg)
![Build](https://img.shields.io/badge/Build-Passing-brightgreen.svg)

## Executive Summary

Welcome to the **Physics-Informed Polymer Informatics & Digital Twin Pipeline**. This repository contains a full-stack PIML (Physics-Informed Machine Learning) architecture designed to predict and optimize Dielectric Breakdown Strength (Eb) and capacitance in advanced polymer materials. By leveraging molecular representations via RDKit (Morgan Fingerprints/PolyBERT) alongside ANSYS Finite Element Analysis (FEA) surrogate modeling, the system accelerates the materials discovery lifecycle. Furthermore, it utilizes Multi-Objective Inverse Design and IoT Digital Twins to dynamically optimize polymer manufacturing and processing conditions.

## Core Architecture (The 3 Pillars)

### Pillar 1: Surrogate Modeling & FEA
Our predictive engine seamlessly bridges quantum-level representations with continuum physics. Using an XGBoost and Multi-Layer Perceptron (MLP) ensemble, the pipeline learns directly from high-fidelity ANSYS finite element simulation data (`code_12_ansys_sweep.py`, `code_13_train_ansys.py`). This allows us to achieve near-FEA accuracy at a fraction of the computational cost, enabling rapid screening of complex polymer spaces.

### Pillar 2: Multi-Objective Inverse Design
Once the forward surrogate models are trained, we perform Virtual High-Throughput Screening (vHTS) coupled with robust L-BFGS-B optimization algorithms (`code_14_inverse_ansys.py`). This approach solves the inverse problem: finding the ideal manufacturing processing conditions (e.g., temperature, crystallinity, applied voltage) and copolymer blend ratios to strictly meet target industrial capacitance constraints.

### Pillar 3: Generative AI & IoT Digital Twin
The pipeline moves beyond existing materials via *De Novo* molecular generation using a Variational Autoencoder (VAE) and Genetic Algorithms (`code_19_vae_discovery.py`). Finally, our architecture incorporates a simulated Raspberry Pi PID controller to stream telemetry data, forming an integrated IoT Digital Twin that actively monitors and optimizes live manufacturing processes based on our ML predictions.

## Publication-Grade Reproducibility

Rigorous software engineering standards have been enforced throughout this repository to guarantee 100% scientific reproducibility across Windows, macOS, and Linux:
- **Global Seed Locking**: All stochastic processes and module-level seeds are strictly locked to `42` using a centralized `enforce_reproducibility` mechanism.
- **OS-Agnostic Paths**: All I/O operations utilize `pathlib` for dynamic, robust path resolution.
- **Enterprise Telemetry**: Standard output via `print()` has been fully eradicated in favor of `PipelineLogger`, ensuring structured, analyzable execution logs for enterprise environments.

## Installation & Deployment (Quick Start)

### Docker Deployment
The recommended and fastest way to run the pipeline is via Docker:

```bash
git clone https://github.com/lenovo-imi/polymer-informatics.git
cd polymer-informatics
docker-compose up --build -d
```

### Local Development (Python Virtual Environment)
To run the project locally on your host machine:

```bash
git clone https://github.com/lenovo-imi/polymer-informatics.git
cd polymer-informatics
python -m venv venv

# Windows
.\venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

pip install -r requirements.txt
```

## Pipeline Execution Guide

To run the pipeline from end-to-end, execute the following commands in order from the root of the repository. Ensure your virtual environment is active.

### 1. Verification & Data Preparation
First, verify your ANSYS Electronics Desktop connection and generate the initial target polymer configurations.
```bash
python codes/code_12_ansys_check.py
python codes/data_pipeline.py
python codes/code_12_prepare_sweep.py
```

### 2. Physics Simulation (ANSYS Maxwell 2D)
Run the automated Finite Element Analysis (FEA) sweep. *Note: This step may take several hours depending on your hardware and virtual library size. It features auto-resume capabilities.*
```bash
python codes/code_12_ansys_sweep.py
python codes/rank_successful_polymers.py
```

### 3. Machine Learning Training
Train the Surrogate Models (XGBoost/MLP ensemble) and advanced Graph Neural Networks (MPNN) using the physics data generated in the previous step.
```bash
python codes/code_13_train_ansys.py
python codes/code_18_gnn_training.py
```

### 4. Advanced Discovery & Optimization
Execute Inverse Design algorithms and De Novo generation (Variational Autoencoder) to discover novel materials that strictly meet industrial constraints.
```bash
python codes/code_14_inverse_ansys.py
python codes/code_17_pareto_optimization.py
python codes/code_19_vae_discovery.py
```

### 5. Reporting & Dashboards
Finally, generate the academic-grade summary report and launch the interactive web dashboard.
```bash
# Generate the final statistical report
python codes/code_15_final_report.py

# Launch the interactive Inverse Design Web UI
streamlit run codes/code_16_dashboard.py
```

*(Optional) Launch the React Web Frontend:*
If you prefer the rich React/Vite frontend over Streamlit, you can start the backend API and the React UI simultaneously using two separate terminal windows.

**Terminal 1 (Start Backend API):**
```bash
uvicorn codes.backend_api:app --reload
```

**Terminal 2 (Start React UI):**
```bash
cd frontend
npm install
npm run dev
```

## Project Structure

```text
codes/
├── adaptive_retry_manager.py       # ANSYS adaptive mesh retry logic
├── ansys_bridge.py                 # Core bridge logic for ANSYS connections
├── ansys_integration.py            # High-level ANSYS integration API
├── backend_api.py                  # FastAPI/REST service backend
├── code_12_ansys_check.py          # Verifies ANSYS environment and license
├── code_12_ansys_sweep.py          # Performs high-throughput ANSYS Maxwell 2D simulations
├── code_12_prepare_sweep.py        # Generates target configs for the ANSYS sweep
├── code_13_train_ansys.py          # Trains the XGBoost/MLP surrogate ensemble on FEA data
├── code_14_inverse_ansys.py        # Runs L-BFGS-B inverse design optimization
├── code_15_final_report.py         # Aggregates results into a final academic report
├── code_16_dashboard.py            # Streamlit dashboard for interactive screening
├── code_17_pareto_optimization.py  # Performs Pareto frontier multi-objective analysis
├── code_18_gnn_training.py         # Message Passing Neural Network (MPNN) feature extraction
├── code_19_vae_discovery.py        # VAE for De Novo polymer generation
├── config.py                       # Global configuration and hyperparameter constants
├── config_manager.py               # Dynamic OS-agnostic configuration and path resolution
├── constants.py                    # Static dictionaries (BACKBONES, LEFT/RIGHT_GROUPS, etc.)
├── cross_validation.py             # Advanced seeded cross-validation routines
├── data_pipeline.py                # Synthetic parameterized dataset generator
├── dataset_composition_manager.py  # Stratified dataset splitting by material class
├── logger_setup.py                 # Production-grade structured logging module (PipelineLogger)
├── model_trainer.py                # Batch-aware machine learning model trainer with checkpointing
├── rank_successful_polymers.py     # Post-processing script to rank simulated candidates
├── reproducibility.py              # Centralized seed-locking and determinism enforcement
└── transformers.py                 # Custom Scikit-Learn transformers (e.g., CollinearityDropper)
```
