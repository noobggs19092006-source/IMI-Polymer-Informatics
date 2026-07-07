import re


class FailureClassifier:
    """Classifies ANSYS simulation errors to apply targeted remediation."""

    def __init__(self):
        self.error_patterns = {
            "mesh_error": [
                re.compile(r"mesh.*failed", re.IGNORECASE),
                re.compile(r"element.*quality", re.IGNORECASE),
                re.compile(r"skewness", re.IGNORECASE),
                re.compile(r"mesh singularity", re.IGNORECASE),
            ],
            "solver_divergence": [
                re.compile(r"diverge", re.IGNORECASE),
                re.compile(r"singular matrix", re.IGNORECASE),
                re.compile(r"ill-condition", re.IGNORECASE),
            ],
            "geometry_error": [
                re.compile(r"invalid geometry", re.IGNORECASE),
                re.compile(r"intersect", re.IGNORECASE),
                re.compile(r"degenerate", re.IGNORECASE),
            ],
            "convergence_fail": [
                re.compile(r"iteration limit", re.IGNORECASE),
                re.compile(r"tolerance not met", re.IGNORECASE),
                re.compile(r"residual", re.IGNORECASE),
            ],
        }

    def diagnose(self, error_msg: str) -> str:
        """Classify failure by parsing error messages and logs."""
        if not error_msg:
            return "unknown"

        error_text = str(error_msg).lower()
        for failure_mode, patterns in self.error_patterns.items():
            if any(pattern.search(error_text) for pattern in patterns):
                return failure_mode

        # Default fallback for unknown issues
        return "unknown"
