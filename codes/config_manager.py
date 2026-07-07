import os
import sys
import json
import logging
import subprocess

try:
    import yaml
except ImportError:
    yaml = None
from typing import Dict, Optional, List
from pathlib import Path
from logger_setup import PipelineLogger

try:
    from codes.input_validation import InputValidator
except ImportError:
    try:
        from input_validation import InputValidator
    except ImportError:
        InputValidator = None

logger = PipelineLogger.get_logger(__name__)


class AnsysPathResolver:
    """Dynamically locate Ansys installation across platforms."""

    WINDOWS_STANDARD_PATHS = [
        r"C:\Program Files\ANSYS Inc\v{version}\ANSYS\bin\ansys{version}",
        r"C:\Program Files (x86)\ANSYS Inc\v{version}\ANSYS\bin\ansys{version}",
    ]

    LINUX_STANDARD_PATHS = [
        "/opt/ansys/v{version}/ansys/bin/ansys{version}",
        "/usr/local/ANSYS/v{version}/ansys/bin/ansys{version}",
        "/home/shared/ansys/v{version}/ansys/bin/ansys{version}",
    ]

    @classmethod
    def _verify_executable(cls, path: str) -> bool:
        """Verify path is actually executable."""
        path_obj = Path(path)

        if not path_obj.exists():
            return False

        if not os.access(path_obj, os.X_OK):
            logger.warning(f"Path exists but is not executable: {path}")
            return False

        return True

    @classmethod
    def resolve_ansys_path(cls, version: str = None) -> Optional[str]:
        """Find Ansys executable using multiple strategies."""

        # Strategy 1: Explicit environment variable
        explicit_path = os.getenv("ANSYS_EXECUTABLE")
        if explicit_path and cls._verify_executable(explicit_path):
            logger.info(f"Found Ansys via ANSYS_EXECUTABLE: {explicit_path}")
            return explicit_path

        # Strategy 2: Standard paths — versions pulled from env var or yaml config
        _version_str = os.getenv("ANSYS_VERSIONS", "2025,2024,2023,2022")
        _supported_versions = [v.strip() for v in _version_str.split(",") if v.strip()]

        platform_paths = (
            cls.WINDOWS_STANDARD_PATHS if sys.platform == "win32" else cls.LINUX_STANDARD_PATHS
        )

        for path_template in platform_paths:
            if version:
                path = path_template.format(version=version)
                if cls._verify_executable(path):
                    return path
            else:
                for v in _supported_versions:
                    candidate = path_template.format(version=v)
                    if cls._verify_executable(candidate):
                        return candidate

        # Strategy 3: Check PATH
        import shutil

        possible_names = ["ansys", "ansys2025", "ansys2024", "ansys2023"]
        for name in possible_names:
            found = shutil.which(name)
            if found:
                return found

        return None


class ConfigurationLoader:
    """Load and validate configuration from multiple sources."""

    @classmethod
    def load_from_file(cls, config_path: str) -> Dict:
        """Load configuration from YAML or JSON file."""
        config_path = Path(config_path)

        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        try:
            with open(config_path, "r") as f:
                if config_path.suffix in [".yaml", ".yml"]:
                    if yaml is None:
                        raise ImportError("PyYAML is not installed.")
                    config_dict = yaml.safe_load(f)
                elif config_path.suffix == ".json":
                    config_dict = json.load(f)
                else:
                    raise ValueError(f"Unsupported config format: {config_path.suffix}")
        except Exception as e:
            if yaml and isinstance(e, yaml.YAMLError):
                raise ValueError(f"Invalid YAML in {config_path}: {e}")
            elif isinstance(e, json.JSONDecodeError):
                raise ValueError(f"Invalid JSON in {config_path}: {e}")
            raise e

        return config_dict

    @classmethod
    def load_configuration(cls) -> Dict:
        """Load configuration from environment variables."""

        ansys_path = AnsysPathResolver.resolve_ansys_path(os.getenv("ANSYS_VERSION"))

        config = {
            "ansys": {
                "executable_path": ansys_path,
                "version": os.getenv("ANSYS_VERSION", "2025.2"),
                "license_server": os.getenv("ANSYS_LICENSE_SERVER", "localhost"),
                "license_port": int(os.getenv("ANSYS_LICENSE_PORT", "1055")),
                "core_count": int(os.getenv("ANSYS_CORE_COUNT", "4")),
                "mesh_resolution": os.getenv("ANSYS_MESH_RESOLUTION", "Standard"),
            },
            "paths": {
                "working_directory": os.getenv("WORK_DIR", os.getcwd()),
                "temp_directory": os.getenv("TEMP_DIR", str(Path.home() / ".polymerinfo" / "temp")),
                "output_directory": os.getenv("OUTPUT_DIR", str(Path.cwd() / "output")),
            },
            "simulation": {
                "max_retries": int(os.getenv("MAX_RETRIES", "3")),
                "random_seed": int(os.getenv("RANDOM_SEED", "42")),
            },
        }

        # Validate Ansys config if validator is available
        if InputValidator is not None:
            is_valid, errors = InputValidator.validate_ansys_config(config["ansys"])
            if not is_valid:
                logger.error(f"Invalid Ansys configuration: {errors}")
                # We could raise an error here, but for now we just log it

        return config


# Global config instance
pipeline_config = ConfigurationLoader.load_configuration()
