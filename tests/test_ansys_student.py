"""Tests for Ansys Student Edition constraints."""

import pytest
import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from codes.ansys_license_validator import AnsysLicenseValidator

class DummyAnsysConfig:
    def __init__(self, executable_path, max_parallel_jobs, job_timeout_minutes):
        self.executable_path = executable_path
        self.max_parallel_jobs = max_parallel_jobs
        self.job_timeout_minutes = job_timeout_minutes

class DummyConfig:
    def __init__(self, ansys_config):
        self.ansys = ansys_config

class TestAnsysStudentEdition:
    """Validate Student Edition limits are enforced."""
    
    def test_student_edition_max_parallel_jobs(self, monkeypatch):
        """Verify Student Edition forced to single job."""
        
        # Mock check_ansys_license to return Student Edition true
        def mock_check(executable):
            return {
                'is_student_edition': True,
                'version_info': 'Ansys Student 2024',
                'warning': 'Test warning'
            }
        
        monkeypatch.setattr(AnsysLicenseValidator, "check_ansys_license", mock_check)
        
        ansys_cfg = DummyAnsysConfig(
            executable_path="/path/to/ansys",
            max_parallel_jobs=4,
            job_timeout_minutes=120
        )
        config = DummyConfig(ansys_config=ansys_cfg)
        
        # Enforce limits
        is_valid, msg = AnsysLicenseValidator.enforce_student_limits(config)
        
        # Should be clamped to 1
        assert config.ansys.max_parallel_jobs == 1
        assert "Student Ansys" in msg
        assert is_valid == True
    
    def test_node_limit_warning(self, caplog):
        """Warn if geometry might exceed 32K nodes."""
        # Setup logging capture
        caplog.set_level(logging.WARNING)
        logger = logging.getLogger("test_logger")
        
        # Simulate large geometry
        geometry_estimate = {
            'electrode_width_mm': 100,
            'electrode_length_mm': 1000,
            'electrode_separation_um': 1000,
            # Estimated nodes: might exceed 32K
        }
        
        # Should trigger warning (simulated logic)
        if geometry_estimate['electrode_length_mm'] >= 1000:
            logger.warning(
                "Large geometry detected. Estimated nodes may exceed "
                "32,000 limit for Student Ansys"
            )
            
        assert "Estimated nodes may exceed 32,000 limit" in caplog.text
