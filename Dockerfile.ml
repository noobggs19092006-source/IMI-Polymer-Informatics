# Dockerfile.ml — Production-ready ML pipeline image
# ============================================================================
# IMPORTANT: ANSYS Handling
# This Docker image is for the ML pipeline ONLY (data processing, training).
#
# Ansys simulation runs OUTSIDE the container because:
#   1. Ansys requires a system license (cannot be containerized)
#   2. Ansys is Windows/Linux specific
#   3. Ansys output is mounted as a volume
#
# Workflow:
#   1. Run Ansys simulations on host/HPC cluster  →  ./results/
#   2. `docker run polymer-ml python -m codes.code_13_train_ansys`
# ============================================================================

# ── Stage 1: Builder ─────────────────────────────────────────────────────────
FROM python:3.10-slim AS builder

WORKDIR /app

# System build deps
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
        git \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps into user space so we can copy them cleanly
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# ── Stage 2: Runtime (minimal) ────────────────────────────────────────────────
FROM python:3.10-slim

# Build arguments (passed from CI)
ARG BUILD_DATE
ARG VCS_REF
ARG VERSION=unknown

LABEL org.opencontainers.image.created="$BUILD_DATE" \
      org.opencontainers.image.revision="$VCS_REF" \
      org.opencontainers.image.version="$VERSION" \
      org.opencontainers.image.title="Polymer Informatics ML Pipeline" \
      org.opencontainers.image.description="ML pipeline for polymer capacitance prediction" \
      org.opencontainers.image.authors="IMI Team"

WORKDIR /app

# Runtime system deps (OpenMP for XGBoost/sklearn)
RUN apt-get update && apt-get install -y --no-install-recommends \
        libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local

# ── Copy ONLY directories that actually exist in the repo ────────────────────
COPY codes/   codes/
COPY config/  config/
COPY main.py  .

# Create runtime directories (results/logs/graphs are mounted as volumes in prod)
RUN mkdir -p results logs graphs files temp

# ── Environment ───────────────────────────────────────────────────────────────
ENV PATH="/root/.local/bin:$PATH" \
    PYTHONPATH="/app" \
    PYTHONUNBUFFERED="1" \
    PYTHONHASHSEED="42"

# ── Non-root user ─────────────────────────────────────────────────────────────
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# ── Health check ──────────────────────────────────────────────────────────────
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD python -c "from codes.config_manager import ConfigurationLoader; ConfigurationLoader.load_configuration()"

ENTRYPOINT ["python", "main.py"]
