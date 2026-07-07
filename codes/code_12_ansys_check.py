import os
from pathlib import Path
from ansys.aedt.core import Desktop
import sys

from codes.reproducibility import enforce_reproducibility
from codes.logger_setup import PipelineLogger
import logging

logger = logging.getLogger(__name__)

# Force UTF-8 for logger output in Windows
sys.stdout.reconfigure(encoding='utf-8')

enforce_reproducibility(42)

_REPO_ROOT = Path(__file__).resolve().parent.parent
project_path = _REPO_ROOT / "Ansys_Connection_Test.aedt"

try:
    # Simplified call for the new ansys-aedt-core 0.27.1
    d = Desktop(version="2025.2", non_graphical=False, student_version=True)
    
    logger.info("✅ Success! Python successfully launched ANSYS Electronics Desktop 2025 R2.")
    logger.info("Current AEDT Version: %s", d.aedt_version_id)
    
    # Close the session safely
    d.release_desktop(True, True)
    logger.info("Session closed safely.")

except Exception as e:
    logger.error("Error: Could not connect to ANSYS.")
    logger.error("Details: %s", str(e))
    logger.error("Please verify that ANSYS is installed correctly and environment variables are set.")
