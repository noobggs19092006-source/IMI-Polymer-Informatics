# FC — Project Cross-Check Review

**Project:** Physics-Informed Polymer Informatics & Digital Twin Pipeline
**Scope reviewed:** entire repo except `venv/`, `frontend/node_modules/`, `.git/` (dependencies)
**Purpose:** pre-investor-presentation sanity check
**Date:** 2026-07-07

---

## TL;DR (read this first)

The **scientific core is real and the ANSYS simulations genuinely ran** (authentic logs, CSVs, graphs, checkpoints). The architecture is coherent and well-organized. However, **several headline claims in docs/reports are not backed by the code**, and a few things are *literally fabricated or non-functional*. For an investor demo these are the high-visibility risks:

1. The **Final Report and the API hardcode performance numbers** (R² = 0.9558, etc.) as static text — they are not computed from the model.
2. The **VAE is self-labeled "NOT scientifically valid for publication"** in its own source, yet is presented as a Phase 5 deliverable.
3. The **"production" Docker image runs a stub** (`main.py`) that never executes the pipeline, and its healthcheck is broken.
4. **CI/CD is decorative** — every lint/test gate passes with `|| true` / `continue-on-error`, and the integration test actually crashes on import while CI reports green.
5. The **frontend shows hardcoded mock data** (fake SMILES, mock results, a fabricated VAE model) instead of live backend data.

None of this is fatal, but it must be reconciled before you present externally. Details below.

---

## GOOD (strengths worth showing)

- **Real, reproducible science.** `codes/reproducibility.py` centralizes seed-locking; `batch.log` proves the ANSYS Maxwell 2D sweep actually executed (Ansys Student v252, Jul 03–04 2026). Artifacts match claimed volumes (1440 sim rows, 551 ranked, 7 graphs, 3 checkpoints).
- **Clean structure.** `codes/constants.py` is a single source of truth; `codes/logger_setup.py` is a genuinely good rotating-file `PipelineLogger`; `codes/resource_manager.py`, `codes/numerical_stability.py` (Decimal-based capacitance), `codes/input_validation.py` (Pydantic), `codes/transformers.py` (`CollinearityDropper`) are solid, well-written modules.
- **Frontend architecture is sound.** React + Vite + TypeScript with proper Zustand store (`useAppStore.ts`), correct API interface definitions (`services/api.ts`), and all 6 phase pages wired in `App.tsx`. Build will compile and render.
- **Some real tests exist.** `tests/test_edge_cases.py` and `tests/test_ansys_student.py::test_student_edition_max_parallel_jobs` are valid and would pass.
- **No leaked secrets.** No API keys/passwords in code; `.env.example` is a safe placeholder; no committed `.env`.
- **Good engineering hygiene files.** `.flake8`, `.pre-commit-config.yaml`, `pyproject.toml` (black/mypy), `requirements.txt` with pinned ranges.
- **`issues and fixes/` docs** show honest debugging history.

---

## OK (minor / cosmetic — fix if time permits)

- **`main.py --config` is parsed but never passed** to `load_configuration()`; config always comes from env vars (so `default_config.yaml` is effectively decorative).
- **Two `MaterialClass` enums** with different values live in `dataset_composition_manager.py` and `cross_validation.py`.
- **Duplicate `CrossValidationByMaterialClass`** in `dataset_composition_manager.py` shadows the real one in `cross_validation.py`.
- **Dead code:** `codes/type_validation.py`, `codes/encoding_utils.py::SafeFileWriter`, `codes/test_predict.py`, `codes/config.py` relative `MODEL_PATH` are unused.
- **Theme contradiction (frontend):** `tailwind.config.js` defines a dark palette per the design prompt, but `index.css` overrides to light mode. Pick one.
- **`.gitignore` does not exclude `results/`, `graphs/`, `files/`, `results/checkpoints/*.pkl`** — large artifacts would be committed (may be intentional, but inconsistent with stated intent).
- **Version drift:** tests mock "Ansys Student 2024", `default_config.yaml` says 2024, `config_manager` default "2025.2", actual run was 2025.2.0.
- **`version.py`** has placeholder author `"Your Team"` / `your-email@company.com`.
- **`config/default_config.yaml`** hardcodes a fake `license_server: ansyslicense.company.com` (not a secret, but a committed reference).
- **Frontend stub endpoints** (`getSearchResults`, `getMetrics`, `validatePolymer`, fake-PDF `exportResults`) exist but are disconnected.
- A few unused imports / props (`Settings` in `App.tsx`, `onExport` not wired in `Phase4Analytics`, `onSelectModel` not synced to store).

---

## BAD (real problems — address before presenting)

### CRITICAL — credibility / "fabricated numbers" risks

- **[C1] Final Report hardcodes metrics.** `codes/code_15_final_report.py:123,223-224,227,360,397,429,495` embeds `R² = 0.9558`, `CV = 0.9073`, `±0.0614`, `MAE 14.68` etc. as literal strings. They are not derived from a live evaluation. If the model trains to different numbers, the report still claims the originals.
- **[C2] API returns fake metrics.** `codes/backend_api.py:131-132` serves `r2: 0.9558` / `0.9528` as hardcoded constants in `/api/models`.
- **[C3] VAE is self-admittedly invalid.** `codes/code_19_vae_discovery.py:245` logs *"gradients are mathematically INCOMPLETE and this model is NOT scientifically valid for publication"*; backprop only updates 2 layers (finite-difference), KL weight 0.001 causes posterior collapse, and "discovered" polymers get *randomly assigned* physical properties unrelated to their SMILES. Yet README + Final Report present it as a deliverable.
- **[C4] Physics fudge factor.** `codes/ansys_bridge.py:95-97` does `pseudo_val = cap * 1e14; if pseudo_val < 100: pseudo_val += 400` — an arbitrary inflation of small capacitance values with no physical basis. README calls this "near-FEA accuracy."

### HIGH — packaging / runs-but-doesn't-work

- **[H1] `main.py` is a stub.** Lines 66-67: `# Placeholder for actual pipeline execution logic` then exits. `Dockerfile.ml` `ENTRYPOINT ["python","main.py"]` therefore runs only license validation and **never runs the pipeline**. The "production-ready" image does nothing.
- **[H2] Docker healthcheck is broken.** `Dockerfile.ml` sets `PYTHONPATH=/app` but there is **no `codes/__init__.py`** (verified), and `config_manager.py` does bare `from logger_setup import` (intra-package import fails outside pytest/conftest). HEALTHCHECK → `ModuleNotFoundError` → container unhealthy.
- **[H3] `docker-compose.yml:16` references `config/production_config.yaml`** which does not exist (only `config/default_config.yaml`). Broken mount reference.
- **[H4] CI is decorative.** `.github` workflows run black/flake8/mypy with `|| true` and unit/integration tests with `continue-on-error: true`. Build badge will be green even on total failure.
- **[H5] Integration test never runs in CI.** `ci.yml` invokes `python tests/run_integration_test.py` with no `codes/` on path → `ModuleNotFoundError` before any test; `continue-on-error` hides it. (Passes only under pytest via conftest.)
- **[H6] Broken integration test calls.** `tests/run_integration_test.py:142` passes a YAML *path* to `DatasetCompositionManager` (expects `min_samples_per_class: int`); `:159` passes a column *name* to `TargetAnalyzer` (expects `target_pf_per_m: float`). These will crash or silently skip.

### MEDIUM — contradictions & fake tests

- **[M1] Fake test.** `tests/test_ansys_student.py::test_node_limit_warning` never calls production code — it logs a warning and asserts on its own text. Proves nothing.
- **[M2] Stubbed test.** `tests/run_integration_test.py:113` (`test_config_load`) is explicitly stubbed ("validator moved/removed").
- **[M3] Final Report numeric inconsistencies:** claims "11 Pareto-optimal polymers" but `results/pareto_optimal_polymers.csv` has 7 rows; references `ansys_ensemble_pipeline.pkl` / `ansys_gnn_pipeline.pkl` which don't exist (only component checkpoints); Appendix run commands omit the `codes/` prefix so they fail as written; CHANGELOG claims 75% success while `Final_Report_ANSYS.md` shows 38.3% (551/1440).
- **[M4] `openfixes.md` self-contradiction.** Claims "zero print() calls across 16 scripts" while the same file lists `print()`-using files; and self-awards "GPA 3.17/4.0 — ACCEPTED FOR PUBLICATION" while marking `pytest` and `mypy` checks as *UNVERIFIED*.
- **[M5] README contradictions** (see table below).
- **[M6] Security anti-pattern.** `codes/backend_api.py:38-43` sets `CORSMiddleware(allow_origins=["*"], allow_credentials=True)` — invalid/browser-rejected combo; a known anti-pattern.
- **[M7] `code_13_train_ansys.py:194` hardcodes `device="cuda"`** → crashes on CPU-only machines.
- **[M8] Destructive `fix_errors.py`** does repo-wide in-place string replacement; never called, but dangerous if run.

### LOW — reproducibility gaps

- **[L1] README claims print() eradicated** — false (`run_pipeline.py`, `code_12_ansys_check.py`, `code_15_final_report.py`, `target_analyzer.py`, `test_predict.py` all use `print()`).
- **[L2] README claims "all stochastic processes locked to 42"** — `enforce_reproducibility(42)` is not called in several entry points (`ansys_integration.py`, `backend_api.py`, `code_12_*`, `code_16_dashboard.py`, `dataset_composition_manager.py`, `resource_manager.py`).
- **[L3] `PYTHONHASHSEED` set too late** to affect the current process (acknowledged in `reproducibility.py` docstring).
- **[L4] `results/metadata.json` is just `{"random_seed": 42}`** — contradicts the rich "Output Registry" the report describes.

---

## Frontend-specific BAD (investor-facing)

- **[F1] `Phase5Results.tsx` renders hardcoded `MOCK_RESULTS`** — investors see static demo data, not real discovery output. Export buttons only `alert()`.
- **[F2] `Phase1Generation.tsx` fabricates fake SMILES** locally (`CCECEC`) and ignores the API response.
- **[F3] `Phase2ModelSelection.tsx` hardcodes 3 model cards** (incl. a VAE with R²=0.8945) while backend `/api/models` returns only 2 (ensemble, gnn). VAE card is fabricated.
- **[F4] Nav/phase desync** — `NAV_LINKS` "Analytics" maps to `phase 4` but `phaseMap` routes it to phase 3; clicking Analytics shows stepper at Inverse Design while rendering Analytics. Phase 4 also has no sidebar item.
- **[F5] ~700 lines of dead animation code** (`PixelSnow*`, `StepperReal`, `StarBorderReal`, `StaggeredMenuReal`, `StepReal`) exported but never rendered.
- **[F6] Fake PDF export** — `exportResults` returns a `Blob` of text labeled `application/pdf`; PDF viewers reject it.
- **[F7] Phase naming mismatch** across `Phase0Overview` (1–6) vs `App.tsx` (0–5) vs design prompt — three different schemes.

---

## README/Docs vs Code contradictions (quick table)

| Doc claim | Reality | Ref |
|---|---|---|
| "XGBoost + MLP ensemble" | Actually MLP + GBR + XGBoost (3-way) | README:14 vs config.py / code_13 |
| "print() eradicated" | Many scripts still print | L1 |
| "All seeds locked to 42" | Not called in several entry points | L2 |
| "Docker: `docker-compose up --build`" | `production_config.yaml` missing; main.py stub; healthcheck broken | H1/H2/H3 |
| "Near-FEA accuracy" | `ansys_bridge` +400 fudge factor | C4 |
| "De Novo VAE generation" | Self-labeled not scientifically valid | C3 |
| R²=0.9558 / CV=0.9073 | Hardcoded text constants | C1/C2 |
| CHANGELOG "success 38%→75%" | Report shows 38.3% | M3 |

---

## Recommended pre-presentation actions (priority order)

1. **Decide the narrative on the VAE.** Either label it clearly as a *research prototype / not for production* in the deck, or pull it from the "deliverables" slide. Do not present C3 as a finished result.
2. **Stop presenting hardcoded metrics as measured.** Either compute them live in the report/API, or visibly footnote them as *target/illustrative* numbers. C1/C2 are the easiest things for a technical investor to catch.
3. **Fix the Docker story.** Make `main.py` actually invoke the pipeline (or change the deck to say "run via `run_pipeline.py` / individual `codes/code_XX` scripts"), add `codes/__init__.py`, and fix `production_config.yaml` reference. Or drop the "production Docker" claim.
4. **Make CI honest** (remove `|| true` / `continue-on-error`) or stop citing the green build as proof of quality.
5. **Wire the frontend to real data** (Phase5 → store, Phase1 → API SMILES, Phase2 → `/api/models`) or present it explicitly as a *UI mockup*, not a live demo.
6. **Reconcile the Final Report numbers** (11 vs 7 Pareto, missing `.pkl`, 38% vs 75%, `codes/` prefix in commands).
7. **Remove `fix_errors.py` and the dead/fake tests** from the repo before sharing.
8. **Add `results/`, `graphs/`, `files/` to `.gitignore`** if they're meant to be build artifacts, not committed deliverables.

---

*No files were modified. This is a read-only review.*
