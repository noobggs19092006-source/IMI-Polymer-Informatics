import json
import os
import pandas as pd
from typing import Dict, Any, Tuple
from simulation_diagnostics import FailureClassifier
import numpy as np
import logging

logger = logging.getLogger(__name__)


class PhysicsValidatedRetryStrategy:
    """Ensure retry strategies are physics-sound."""

    MESH_REFINEMENT_BOUNDS = {
        "min_element_size": 1e-6,
        "max_element_size": 1e-2,
    }

    SOLVER_PARAMETER_BOUNDS = {"voltage": (0.1, 1000), "thickness_nm": (10, 100000)}

    @staticmethod
    def validate_remesh_strategy(params: Dict, attempt: int) -> Dict:
        """Ensure mesh refinement doesn't violate physics constraints."""
        current_size = params.get("mesh_size_factor", 1.0)
        min_size = PhysicsValidatedRetryStrategy.MESH_REFINEMENT_BOUNDS["min_element_size"]

        refined_size = current_size * (0.8**attempt)

        if refined_size < min_size:
            logger.warning(f"Mesh refinement would exceed limit. Clamping at {min_size}")
            refined_size = min_size

        params["mesh_size_factor"] = refined_size
        return params

    @staticmethod
    def validate_solver_strategy(params: Dict, attempt: int) -> Dict:
        """Ensure solver adjustments stay within bounds."""
        for param, (
            min_val,
            max_val,
        ) in PhysicsValidatedRetryStrategy.SOLVER_PARAMETER_BOUNDS.items():
            if param in params:
                current = params[param]
                if current < min_val or current > max_val:
                    params[param] = np.clip(current, min_val, max_val)
                    logger.warning(
                        f"Parameter {param}={current} out of bounds [{min_val}, {max_val}]. Clamped."
                    )
        return params


class EnhancedSimulationManager:
    """Manages adaptive retry logic for ANSYS simulations based on diagnosed failure modes."""

    def __init__(self, output_dir: str = "../results"):
        self.output_dir = output_dir
        self.failure_log = []
        self.classifier = FailureClassifier()
        self.retry_strategies = {
            "mesh_error": self._remesh_adaptive,
            "solver_divergence": self._adjust_solver_params,
            "geometry_error": self._validate_geometry,
            "convergence_fail": self._refine_mesh_locally,
            "unknown": self._default_retry,
        }
        os.makedirs(self.output_dir, exist_ok=True)

    def diagnose_and_adapt(
        self, error: Exception, params: Dict[str, Any], attempt: int, max_retries: int
    ) -> Tuple[bool, Dict[str, Any], str]:
        """Diagnose error and return adapted parameters. Returns (should_retry, new_params, failure_mode)."""
        failure_mode = self.classifier.diagnose(str(error))

        log_entry = {
            "attempt": attempt,
            "failure_mode": failure_mode,
            "error_message": str(error),
            "params_before": dict(params),
        }
        self.failure_log.append(log_entry)

        if attempt >= max_retries:
            return False, params, failure_mode

        strategy_fn = self.retry_strategies.get(failure_mode, self._default_retry)
        new_params = strategy_fn(params, attempt)

        return True, new_params, failure_mode

    def _remesh_adaptive(self, params: Dict[str, Any], attempt: int) -> Dict[str, Any]:
        """Adaptively reduce mesh size or adjust thickness backoff."""
        thickness = params.get("thickness_nm", 1000)
        backoff_factor = params.get("backoff_factor", 0.1) * (1.2**attempt)
        params["thickness_nm"] = thickness + (thickness * backoff_factor)

        # Apply physics bounds validation
        params = PhysicsValidatedRetryStrategy.validate_remesh_strategy(params, attempt)
        params = PhysicsValidatedRetryStrategy.validate_solver_strategy(params, attempt)
        return params

    def _adjust_solver_params(self, params: Dict[str, Any], attempt: int) -> Dict[str, Any]:
        """Adjust solver settings for stability."""
        params["voltage"] = params.get("voltage", 100) * 0.9  # Reduce stress
        params = PhysicsValidatedRetryStrategy.validate_solver_strategy(params, attempt)
        return params

    def _validate_geometry(self, params: Dict[str, Any], attempt: int) -> Dict[str, Any]:
        """Validate and repair geometry before retry."""
        thickness = params.get("thickness_nm", 1000)
        params["thickness_nm"] = thickness * 1.1  # Thicker layer might heal geometry
        params = PhysicsValidatedRetryStrategy.validate_solver_strategy(params, attempt)
        return params

    def _refine_mesh_locally(self, params: Dict[str, Any], attempt: int) -> Dict[str, Any]:
        """Refine mesh in high-gradient regions."""
        params["mesh_resolution"] = "Fine" if attempt > 1 else "Standard"
        return params

    def _default_retry(self, params: Dict[str, Any], attempt: int) -> Dict[str, Any]:
        thickness = params.get("thickness_nm", 1000)
        params["thickness_nm"] = thickness * 1.1
        return params

    def save_failure_report(self):
        """Generate detailed failure analysis for post-mortem."""
        report_path = os.path.join(self.output_dir, "simulation_diagnostics.json")
        with open(report_path, "w") as f:
            json.dump(self.failure_log, f, indent=4)

        if self.failure_log:
            df = pd.DataFrame(self.failure_log)
            summary_path = os.path.join(self.output_dir, "failure_summary.txt")
            with open(summary_path, "w") as f:
                f.write("SIMULATION FAILURE ANALYSIS REPORT\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Total Failures Logged: {len(df)}\n")
                f.write(f"Failure Mode Distribution:\n{df['failure_mode'].value_counts()}\n\n")
