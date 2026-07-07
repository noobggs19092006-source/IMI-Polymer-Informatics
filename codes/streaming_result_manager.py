import json
import logging
from pathlib import Path
from typing import Dict, Optional
import numpy as np
import hashlib

logger = logging.getLogger(__name__)


class StreamingResultManager:
    """Stream results to disk without loading all in memory."""

    def __init__(self, output_file: str, batch_size: int = 1000):
        self.output_file = output_file
        self.batch_size = batch_size
        self.batch = []
        self.writer = None
        self.total_results = 0
        self.batches_written = 0
        self.samples_seen = set()
        self.file_hash = hashlib.sha256()

    def __enter__(self):
        self.writer = open(self.output_file, "w")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.batch:
            self._flush_batch()

        final_checksum = self.file_hash.hexdigest()

        summary = self.get_summary()
        summary["checksum_sha256"] = final_checksum

        summary_file = Path(self.output_file).parent / "results_summary.json"
        with open(summary_file, "w") as f:
            json.dump(summary, f, indent=2)

        self.writer.close()
        logger.info(f"Results file checksum: {final_checksum}")

    def add_result(self, sample_id: str, capacitance: float, validate: bool = True):
        """Add result with validation and track metadata."""
        if validate:
            if sample_id is None or len(str(sample_id)) == 0:
                raise ValueError(f"Invalid sample_id: {sample_id}")

            if not isinstance(capacitance, (int, float)):
                raise TypeError(f"Capacitance must be numeric, got {type(capacitance)}")

            if np.isnan(capacitance):
                raise ValueError(f"Capacitance is NaN for sample {sample_id}")

            if np.isinf(capacitance):
                raise ValueError(f"Capacitance is infinite for sample {sample_id}")

            if capacitance < 0:
                raise ValueError(
                    f"Capacitance cannot be negative. " f"Sample {sample_id}: {capacitance} pF/m"
                )

            if capacitance > 1e6:
                logger.warning(
                    f"Unusually large capacitance for {sample_id}: {capacitance} pF/m. "
                    f"Verify this is intentional."
                )

        if sample_id in self.samples_seen:
            raise ValueError(f"Duplicate sample_id: {sample_id}")

        self.samples_seen.add(sample_id)
        self.batch.append((sample_id, capacitance))
        self.total_results += 1

        if len(self.batch) >= self.batch_size:
            self._flush_batch()

    def _flush_batch(self):
        """Write batch to disk and clear memory."""
        if not self.writer:
            raise RuntimeError("StreamingResultManager must be used as a context manager.")

        for sample_id, capacitance in self.batch:
            line = f"{sample_id},{capacitance:.2f}\n"
            self.writer.write(line)
            self.file_hash.update(line.encode("utf-8"))

        self.batches_written += 1
        self.batch.clear()

    def get_summary(self) -> Dict:
        """Get summary of results written."""
        return {
            "total_results": self.total_results,
            "batches_written": self.batches_written,
            "unique_samples": len(self.samples_seen),
            "output_file": str(self.output_file),
        }
