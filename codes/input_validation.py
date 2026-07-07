import os
import argparse
from typing import Dict, Any, List, Tuple
from pydantic import BaseModel, Field, ValidationError, field_validator, model_validator
import logging

logger = logging.getLogger(__name__)


class SimulationParameters(BaseModel):
    """Validated simulation parameters with cross-field checks."""

    material_permittivity: float
    electrode_width_mm: float
    electrode_length_mm: float
    electrode_separation_um: float

    @field_validator("material_permittivity")
    def validate_permittivity(cls, v):
        """Validate material relative permittivity."""
        if v <= 0:
            raise ValueError(
                f"Material permittivity must be positive. Got: {v}. "
                f"Examples: Air=1.0, Paper=3.7, Water=80.0"
            )

        if v > 1000:
            raise ValueError(
                f"Material permittivity {v} exceeds typical range [0.5, 1000]. "
                f"High-k materials rarely exceed 1000. "
                f"Please verify input data."
            )

        if v < 1:
            raise ValueError(
                f"Permittivity {v} is below vacuum (1.0). " f"This is physically impossible."
            )

        if v > 100 and v < 1000:
            logger.warning(
                f"High permittivity detected: {v}. "
                f"Verify this is intentional (typical range: 1-50)"
            )

        return v

    @model_validator(mode="after")
    def validate_electrode_geometry(self):
        """Validate geometric constraints."""
        width = self.electrode_width_mm
        length = self.electrode_length_mm
        sep = self.electrode_separation_um

        if width and length and width > length:
            raise ValueError(f"Electrode width ({width}mm) cannot exceed length ({length}mm)")

        if width and sep and (sep / 1000) > width / 10:
            raise ValueError(
                f"Separation ({sep}um) is too large relative to width ({width}mm). "
                f"Expected separation < width/10"
            )

        aspect_ratio = length / width if width > 0 else 0
        if aspect_ratio > 100:
            raise ValueError(
                f"Aspect ratio {aspect_ratio:.1f} exceeds typical limit of 100. "
                f"Consider reducing length or increasing width."
            )
        return self

    class Config:
        validate_assignment = True


class SolverSettings(BaseModel):
    voltage: float = 100.0


class MeshSettings(BaseModel):
    refinement_level: int = 1


class SimulationConfig(BaseModel):
    """Validated simulation configuration."""

    parameters: SimulationParameters
    solver_settings: SolverSettings
    mesh_settings: MeshSettings

    @model_validator(mode="after")
    def validate_solver_geometry_compatibility(self):
        """Ensure solver and geometry are compatible."""
        params = self.parameters
        solver = self.solver_settings
        mesh = self.mesh_settings

        min_dimension_mm = min(params.electrode_width_mm, params.electrode_separation_um / 1000)

        if min_dimension_mm < 0.01 and mesh.refinement_level < 3:
            raise ValueError(
                f"Geometry very small ({min_dimension_mm}mm) requires "
                f"high mesh refinement (>=3), got {mesh.refinement_level}"
            )

        max_dimension_mm = max(params.electrode_width_mm, params.electrode_length_mm)

        if max_dimension_mm > 100 and mesh.refinement_level > 5:
            logger.warning(
                f"Large geometry ({max_dimension_mm}mm) with very fine mesh "
                f"(level {mesh.refinement_level}) will take very long to solve"
            )

        return self


class AnsysRuntimeConfig(BaseModel):
    """Pydantic model for rigorous input validation of ANSYS configuration."""

    version: str = Field(
        pattern=r"^20\d{2}\.[1-2]$", description="Ansys version format like 2024.1 or 2025.2"
    )
    core_count: int = Field(ge=1, le=128, description="Number of cores to allocate")
    license_port: int = Field(ge=1, le=65535, description="Valid port number for licensing")
    license_server: str = Field(min_length=1, description="License server hostname or IP")
    mesh_resolution: str = Field(
        pattern=r"^(Standard|Fine|Coarse)$", description="Mesh quality level"
    )


class InputValidator:
    """Validates runtime inputs and environment configurations."""

    @staticmethod
    def validate_ansys_config(config_dict: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate an Ansys config dictionary against the schema."""
        try:
            AnsysRuntimeConfig(**config_dict)
            return True, []
        except ValidationError as e:
            errors = [f"{err['loc'][0]}: {err['msg']}" for err in e.errors()]
            return False, errors

    @staticmethod
    def validate_file_path(
        path: str, require_exists: bool = True, expected_ext: str = None
    ) -> bool:
        """Validate paths provided as CLI arguments."""
        if not path:
            return False

        if require_exists and not os.path.exists(path):
            return False

        if expected_ext and not path.endswith(expected_ext):
            return False

        return True
