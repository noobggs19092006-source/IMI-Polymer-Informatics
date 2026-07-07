import sys
import logging
import argparse
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent))
# Add codes directory to Python path for internal module resolution
sys.path.insert(0, str(Path(__file__).parent / 'codes'))

from codes.config_manager import ConfigurationLoader
from codes.ansys_license_validator import AnsysLicenseValidator
from codes.logger_setup import PipelineLogger

def check_ansys_student_edition(config):
    """Warn user if Ansys Student Edition detected."""
    logger = logging.getLogger(__name__)
    
    try:
        ansys_executable = config.get('ansys', {}).get('executable_path', 'ansys') if isinstance(config, dict) else getattr(getattr(config, 'ansys', None), 'executable_path', 'ansys')
        license_info = AnsysLicenseValidator.check_ansys_license(ansys_executable)
        
        if license_info.get('is_student_edition'):
            logger.warning(
                "\n" + "=" * 80
                + "\n⚠️  ANSYS STUDENT EDITION DETECTED"
                + "\n" + "=" * 80
                + "\nLimitations:"
                + "\n  - Max 32,000 nodes per simulation"
                + "\n  - Single-threaded only (max_parallel_jobs = 1)"
                + "\n  - Educational use only (not commercial)"
                + "\n  - License expires after 12 months"
                + "\n"
                + "\nFor production deployment, upgrade to commercial license."
                + "\nSee README.md for details."
                + "\n" + "=" * 80 + "\n"
            )
    except Exception as e:
        logger.debug(f"Could not check Ansys edition: {e}")

def main():
    parser = argparse.ArgumentParser(description="Polymer Informatics Pipeline")
    parser.add_argument("--config", type=str, help="Path to config file", default="codes/default_config.yaml")
    parser.add_argument("--mode", type=str, help="Pipeline mode (ml, data-processing, training, validation)", default="all")
    args = parser.parse_args()
    
    PipelineLogger.setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info(f"Starting pipeline in {args.mode} mode")
    
    config = ConfigurationLoader.load_configuration()
    
    check_ansys_student_edition(config)
    
    # Validate Ansys license
    is_valid, message = AnsysLicenseValidator.enforce_student_limits(config)
    logger.info(message)
    
    if not is_valid:
        logger.error("Ansys license validation failed")
        sys.exit(1)
        
    logger.info("Pipeline configuration validated successfully.")
    
    # Placeholder for actual pipeline execution logic
    logger.info("Pipeline execution finished.")

if __name__ == "__main__":
    main()
