import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import sys
import os

# Ensure codes directory is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'codes')))

from data_validation import validate_data_integrity
from numerical_stability import NumericallyStableCalculator
from input_validation import SimulationParameters

class TestEdgeCases:
    """Test boundary conditions and edge cases."""
    
    def test_empty_dataframe_validation(self):
        """Validate empty DataFrame handling."""
        empty_df = pd.DataFrame()
        is_valid, result = validate_data_integrity(empty_df)
        assert len(result) == 0
        assert is_valid == False
    
    def test_single_row_dataframe(self):
        """Validate single-row DataFrame."""
        single_df = pd.DataFrame({'value': [1.0]})
        is_valid, result = validate_data_integrity(single_df)
        assert len(result) == 1
        assert is_valid == True
    
    def test_extreme_capacitance_values(self):
        """Test numerical stability with extreme values."""
        
        # Very large permittivity
        result_large = NumericallyStableCalculator.calculate_capacitance(1000, 1e-6, 1e-9)
        assert result_large > 0 and not np.isnan(float(result_large))
        
        # Very small permittivity
        result_small = NumericallyStableCalculator.calculate_capacitance(0.1, 1e-6, 1e-9)
        assert result_small > 0 and not np.isnan(float(result_small))
        
        # Edge case: division by very small number
        result_edge = NumericallyStableCalculator.calculate_capacitance(1, 1e-10, 1e-10)
        assert not np.isinf(float(result_edge))
    
    def test_pydantic_validation_edge_cases(self):
        """Test Pydantic validators with edge values."""
        
        # Minimum valid permittivity
        params = SimulationParameters(
            material_permittivity=1.0,
            electrode_width_mm=0.1,
            electrode_length_mm=1.0,
            electrode_separation_um=10
        )
        assert params.material_permittivity == 1.0
        
        # Maximum valid permittivity
        params = SimulationParameters(
            material_permittivity=999,
            electrode_width_mm=100,
            electrode_length_mm=1000,
            electrode_separation_um=1000
        )
        assert params.material_permittivity == 999
        
        # Should reject invalid values
        with pytest.raises(ValueError):
            SimulationParameters(
                material_permittivity=-1,  # Invalid
                electrode_width_mm=1.0,
                electrode_length_mm=10.0,
                electrode_separation_um=100
            )
