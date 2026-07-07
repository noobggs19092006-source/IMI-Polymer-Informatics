import os
import shutil
import logging
from contextlib import contextmanager
from pathlib import Path

from codes.reproducibility import enforce_reproducibility
enforce_reproducibility(42)
logger = logging.getLogger(__name__)


@contextmanager
def managed_temp_directory(temp_dir: str, verify_cleanup: bool = True):
    """
    Context manager that ensures a temporary directory is created before yielding
    and cleaned up (deleted) upon exit, regardless of success or failure.
    """
    path = Path(temp_dir)
    try:
        path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created temporary directory: {path}")
        yield str(path)
    finally:
        if path.exists():
            try:
                shutil.rmtree(path)
                logger.info(f"Cleaned up temporary directory: {path}")
                if verify_cleanup and path.exists():
                    raise RuntimeError(f"Failed to cleanup {path} - directory still exists")
            except Exception as e:
                logger.error(f"Error during cleanup of {path}: {e}")
                if verify_cleanup:
                    raise


@contextmanager
def managed_ansys_job(m2d_instance):
    """
    Context manager for Ansys Maxwell 2D instances or Mapdl instances to ensure
    resources are closed or released properly on completion or error.
    """
    try:
        yield m2d_instance
    finally:
        try:
            if hasattr(m2d_instance, "release_desktop"):
                # Crucial stability fix: False, False keeps desktop open but releases gRPC
                m2d_instance.release_desktop(False, False)
                logger.info("Released Ansys Desktop.")
            elif hasattr(m2d_instance, "exit"):
                m2d_instance.exit()
                logger.info("Exited Ansys Mapdl instance.")
        except Exception as e:
            logger.error(f"Failed to cleanly release Ansys job resources: {e}")
            os.system("taskkill /F /IM ansysedt.exe /T >nul 2>&1")
            os.system("taskkill /F /IM ansysedtsv.exe /T >nul 2>&1")
