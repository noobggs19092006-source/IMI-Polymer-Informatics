import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from scipy.stats import spearmanr
import os


class TheoreticalValidation:
    """Compare Ansys results against analytical formulas."""

    @staticmethod
    def parallel_plate_capacitance(
        permittivity_r: float, area_m2: float, separation_m: float
    ) -> float:
        """Analytical solution for parallel plate capacitor. Returns pF."""
        epsilon_0 = 8.854e-12  # F/m
        return (permittivity_r * epsilon_0 * area_m2 / separation_m) * 1e12

    def compare_simulated_vs_analytical(self, df: pd.DataFrame) -> dict:
        """Check if Ansys deviates significantly from theory."""
        # Assuming area is 1cm x 1cm = 0.0001 m2 (from ansys setup)
        area_m2 = 0.0001

        df["theoretical_capacitance_pF"] = df.apply(
            lambda row: self.parallel_plate_capacitance(
                row.get("dielectric_constant", row.get("material_permittivity", 1.0)),
                area_m2,
                row.get("final_thickness_nm", row.get("thickness_nm", 1000)) * 1e-9,
            ),
            axis=1,
        )

        # simulated is per meter (pF/m), so we convert theoretical to pF/m by dividing by length (0.01m)
        df["theoretical_capacitance_pf_per_m"] = df["theoretical_capacitance_pF"] / 0.01

        sim_cap = df.get("sim_capacitance_F", df.get("capacitance_pf_per_m", 0))
        # Note: if sim_capacitance_F is in Farads, convert to pF/m by multiplying by 1e12 and dividing by length (0.01m)
        if "sim_capacitance_F" in df.columns:
            sim_cap = df["sim_capacitance_F"] * 1e12 / 0.01

        df["deviation_percent"] = (
            (sim_cap - df["theoretical_capacitance_pf_per_m"])
            / df["theoretical_capacitance_pf_per_m"]
        ) * 100

        return {
            "mean_deviation": df["deviation_percent"].mean(),
            "max_deviation": df["deviation_percent"].max(),
            "samples_within_5_percent": (abs(df["deviation_percent"]) <= 5).sum(),
            "samples_within_10_percent": (abs(df["deviation_percent"]) <= 10).sum(),
        }


class TargetAnalyzer:
    def __init__(self, df: pd.DataFrame, target_pf_per_m: float = 200.0):
        self.df = df
        self.target_pf_per_m = target_pf_per_m

        # Normalize capacitance columns
        if "sim_capacitance_F" in self.df.columns:
            self.df["capacitance_pf_per_m"] = self.df["sim_capacitance_F"] * 1e12 / 0.01

    def analyze_achievement_gap(self) -> dict:
        results = {}
        results["distribution"] = self._analyze_distribution()
        results["sensitivity"] = self._calculate_parameter_sensitivity()
        results["physics_check"] = self._validate_physics_constraints()
        return results

    def _analyze_distribution(self) -> dict:
        cap = self.df["capacitance_pf_per_m"]
        return {
            "mean": cap.mean(),
            "median": cap.median(),
            "std": cap.std(),
            "min": cap.min(),
            "max": cap.max(),
            "percentile_90": cap.quantile(0.90),
            "percentile_95": cap.quantile(0.95),
            "target_achievement_rate": (cap >= self.target_pf_per_m).mean(),
            "achievement_gap": self.target_pf_per_m - cap.mean(),
            "gap_to_max": self.target_pf_per_m - cap.max(),
        }

    def _calculate_parameter_sensitivity(self) -> dict:
        numeric_df = self.df.select_dtypes(include=[np.number])
        input_cols = [
            col
            for col in numeric_df.columns
            if col not in ["capacitance_pf_per_m", "sim_capacitance_F", "sim_status"]
        ]
        if not input_cols:
            return {}

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(numeric_df[input_cols].fillna(0))
        y = numeric_df["capacitance_pf_per_m"].fillna(0).values

        correlations = {}
        for i, col in enumerate(input_cols):
            corr, p_value = spearmanr(X_scaled[:, i], y)
            if not np.isnan(corr):
                correlations[col] = {
                    "correlation": float(corr),
                    "p_value": float(p_value),
                    "significance": "p<0.05" if p_value < 0.05 else "not_significant",
                }

        return dict(
            sorted(correlations.items(), key=lambda x: abs(x[1]["correlation"]), reverse=True)
        )

    def _validate_physics_constraints(self) -> dict:
        checks = {}
        # Capacitance should increase with permittivity
        perm_col = (
            "dielectric_constant"
            if "dielectric_constant" in self.df.columns
            else "material_permittivity"
        )
        if perm_col in self.df.columns:
            corr = self.df[perm_col].corr(self.df["capacitance_pf_per_m"])
            checks["permittivity_correlation"] = {
                "expected_direction": "positive",
                "observed_correlation": corr,
                "status": "PASS" if corr > 0.5 else "FAIL",
            }

        # Capacitance should decrease with thickness
        thick_col = (
            "final_thickness_nm" if "final_thickness_nm" in self.df.columns else "thickness_nm"
        )
        if thick_col in self.df.columns:
            corr = self.df[thick_col].corr(self.df["capacitance_pf_per_m"])
            checks["separation_correlation"] = {
                "expected_direction": "negative",
                "observed_correlation": corr,
                "status": "PASS" if corr < -0.5 else "FAIL",
            }
        return checks

    def generate_diagnostic_report(self, output_file: str):
        analysis = self.analyze_achievement_gap()
        theory = TheoreticalValidation().compare_simulated_vs_analytical(self.df)

        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, "w") as f:
            f.write("CAPACITANCE TARGET ACHIEVEMENT ANALYSIS\n")
            f.write("=" * 70 + "\n\n")

            dist = analysis["distribution"]
            f.write("1. DISTRIBUTION ANALYSIS\n")
            f.write("-" * 70 + "\n")
            f.write(f"Mean Capacitance:        {dist['mean']:.1f} pF/m\n")
            f.write(f"Target Capacitance:      {self.target_pf_per_m:.1f} pF/m\n")
            f.write(f"Gap (Target - Mean):     {dist['achievement_gap']:.1f} pF/m\n")
            f.write(f"Achievement Rate:        {dist['target_achievement_rate']*100:.1f}%\n")
            f.write(f"Maximum Observed:        {dist['max']:.1f} pF/m\n")
            f.write(f"Gap to Maximum:          {dist['gap_to_max']:.1f} pF/m\n\n")

            f.write("2. PARAMETER SENSITIVITY RANKING\n")
            f.write("-" * 70 + "\n")
            for param, data in list(analysis.get("sensitivity", {}).items())[:5]:
                f.write(f"{param:.<30} correlation: {data['correlation']:>6.3f}\n")
            f.write("\n")

            f.write("3. PHYSICS VALIDATION (ANALYTICAL VS SIMULATED)\n")
            f.write("-" * 70 + "\n")
            f.write(f"Mean Deviation from Theory: {theory['mean_deviation']:.2f}%\n")
            f.write(f"Max Deviation from Theory:  {theory['max_deviation']:.2f}%\n")
            f.write(f"Samples within 5%:          {theory['samples_within_5_percent']}\n")
            f.write(f"Samples within 10%:         {theory['samples_within_10_percent']}\n\n")

            f.write("4. CONSTRAINT CHECKS\n")
            f.write("-" * 70 + "\n")
            for check_name, result in analysis.get("physics_check", {}).items():
                status = "✓ PASS" if result["status"] == "PASS" else "✗ FAIL"
                f.write(f"{check_name:.<40} {status}\n")


if __name__ == "__main__":
    csv_path = "../results/ansys_simulation_results.csv"
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        if "sim_status" in df.columns:
            df = df[df["sim_status"] == "Success"]

        if len(df) > 0:
            analyzer = TargetAnalyzer(df)
            analyzer.generate_diagnostic_report("../results/target_achievement_analysis.txt")
            print(
                "Target achievement analysis generated at ../results/target_achievement_analysis.txt"
            )
        else:
            print("No successful simulations found to analyze.")
    else:
        print(f"Data file not found: {csv_path}")
