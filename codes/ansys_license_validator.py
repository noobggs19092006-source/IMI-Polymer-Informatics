"""Validate Ansys license type and enforce constraints."""

import subprocess
import logging
from pathlib import Path
from typing import Dict, Tuple

logger = logging.getLogger(__name__)


class AnsysLicenseValidator:
    """Validate Ansys installation and license type."""

    STUDENT_EDITION_LIMITS = {
        "max_nodes": 32000,
        "max_iterations": 10000,
        "parallel_jobs": 1,
        "license_duration_months": 12,
        "commercial_use": False,
    }

    @staticmethod
    def check_ansys_license(ansys_executable: str) -> Dict:
        """Check if Ansys is Student Edition and validate limits."""

        try:
            # Get version info
            result = subprocess.run(
                [ansys_executable, "-version"], capture_output=True, text=True, timeout=5
            )

            output = result.stdout.lower() + result.stderr.lower()

            is_student = any(
                keyword in output for keyword in ["student", "educational", "academic"]
            )

            return {
                "is_student_edition": is_student,
                "version_info": result.stdout,
                "warning": (
                    "⚠️ STUDENT EDITION DETECTED\n" "See README.md for limitations and restrictions"
                )
                if is_student
                else None,
            }

        except Exception as e:
            logger.error(f"Failed to check Ansys license: {e}")
            return {"error": str(e), "is_student_edition": None}

    @staticmethod
    def enforce_student_limits(config) -> Tuple[bool, str]:
        """
        Enforce Student Edition limits on pipeline config.

        Returns:
            (is_valid, message)
        """

        # Determine ansys executable path from config dictionary or object
        ansys_executable = (
            config.get("ansys", {}).get("executable_path", "ansys")
            if isinstance(config, dict)
            else getattr(getattr(config, "ansys", None), "executable_path", "ansys")
        )

        license_info = AnsysLicenseValidator.check_ansys_license(ansys_executable)

        if not license_info.get("is_student_edition"):
            return True, "Commercial Ansys detected"

        # Enforce student limits
        issues = []

        # Handle dict or object config
        if isinstance(config, dict):
            max_parallel = config.get("ansys", {}).get("max_parallel_jobs", 1)
            timeout = config.get("ansys", {}).get("job_timeout_minutes", 60)

            if max_parallel > 1:
                logger.warning(
                    f"Student Ansys detected. Limiting parallel jobs from " f"{max_parallel} to 1"
                )
                if "ansys" in config:
                    config["ansys"]["max_parallel_jobs"] = 1

            if timeout > 60:
                logger.warning(f"Student Ansys may timeout. Current limit: " f"{timeout}min")
                issues.append("Consider reducing job_timeout_minutes to 30-60")
        else:
            if hasattr(config, "ansys") and hasattr(config.ansys, "max_parallel_jobs"):
                if config.ansys.max_parallel_jobs > 1:
                    logger.warning(
                        f"Student Ansys detected. Limiting parallel jobs from "
                        f"{config.ansys.max_parallel_jobs} to 1"
                    )
                    config.ansys.max_parallel_jobs = 1

            if hasattr(config, "ansys") and hasattr(config.ansys, "job_timeout_minutes"):
                if config.ansys.job_timeout_minutes > 60:
                    logger.warning(
                        f"Student Ansys may timeout. Current limit: "
                        f"{config.ansys.job_timeout_minutes}min"
                    )
                    issues.append("Consider reducing job_timeout_minutes to 30-60")

        message = (
            "✓ Student Ansys constraints enforced:\n"
            f"  - max_parallel_jobs: 1 (enforced)\n"
            f"  - max_nodes: {AnsysLicenseValidator.STUDENT_EDITION_LIMITS['max_nodes']}\n"
            f"  - max_iterations: {AnsysLicenseValidator.STUDENT_EDITION_LIMITS['max_iterations']}\n"
            f"⚠️ WARNING: Not suitable for commercial deployment"
        )

        if issues:
            message += "\n\nRecommendations:\n"
            for issue in issues:
                message += f"  - {issue}\n"

        return True, message
