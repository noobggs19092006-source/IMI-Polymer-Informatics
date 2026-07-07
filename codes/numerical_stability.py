import decimal
from decimal import Decimal, getcontext
import math
import numpy as np
from dataclasses import dataclass

# Set precision to maintain numerical stability during capacitor calculations
getcontext().prec = 50


@dataclass
class CapacitanceResult:
    """Capacitance calculation with uncertainty."""

    value: float
    uncertainty: float  # Absolute
    uncertainty_percent: float
    confidence_level: float = 0.95  # 95% CI

    def meets_target(self, target: float, margin: float = 0.0) -> bool:
        """Check if result meets target within uncertainty."""
        lower_bound = self.value - (self.uncertainty * 1.96)
        return lower_bound >= (target - margin)

    def __str__(self) -> str:
        return f"{self.value:.2f} ± {self.uncertainty:.2f} pF ({self.uncertainty_percent:.1f}%)"


class NumericallyStableCalculator:
    """Provides numerically stable calculations for physical quantities using Decimal."""

    EPSILON_0 = Decimal("8.8541878128e-12")  # F/m

    def __init__(self, assumed_solver_accuracy: float = 0.05):
        """
        assumed_solver_accuracy: Estimated Ansys solver accuracy (e.g., 5%)
        """
        self.solver_accuracy = assumed_solver_accuracy

    @classmethod
    def calculate_capacitance(
        cls, permittivity_r: float, area_m2: float, separation_m: float
    ) -> Decimal:
        """
        Calculate capacitance C = (ε_r * ε_0 * A) / d with stable decimal precision.
        Returns capacitance in Farads.
        """
        eps_r = Decimal(str(permittivity_r))
        a_m2 = Decimal(str(area_m2))
        d_m = Decimal(str(separation_m))

        if d_m <= 0:
            raise ValueError("Separation distance must be > 0")

        capacitance = (eps_r * cls.EPSILON_0 * a_m2) / d_m
        return capacitance

    def calculate_capacitance_with_uncertainty(
        self, epsilon_r: float, area_m2: float, separation_m: float
    ) -> CapacitanceResult:
        """Calculate capacitance with uncertainty propagation."""
        capacitance_f = self.calculate_capacitance(epsilon_r, area_m2, separation_m)
        capacitance_pf = float(capacitance_f * Decimal("1e12"))

        # Uncertainty propagation (assuming solver accuracy each input)
        uncertainty_relative = np.sqrt(3 * (self.solver_accuracy**2))
        uncertainty_absolute = capacitance_pf * uncertainty_relative

        return CapacitanceResult(
            value=capacitance_pf,
            uncertainty=uncertainty_absolute,
            uncertainty_percent=uncertainty_relative * 100,
        )

    @classmethod
    def threshold_compare(cls, val1: float, val2: float, tolerance: float = 1e-9) -> bool:
        """Safe comparison of floating point numbers with tolerance."""
        return abs(Decimal(str(val1)) - Decimal(str(val2))) <= Decimal(str(tolerance))
