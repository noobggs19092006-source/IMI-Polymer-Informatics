import logging
import os
import sys
import time
from functools import wraps
from logging.handlers import RotatingFileHandler
from datetime import datetime
from contextvars import ContextVar
from typing import Dict, Any, Callable

# Context variables for tracing
_session_id = ContextVar("session_id", default=None)
_job_id = ContextVar("job_id", default=None)


class SessionAwareFormatter(logging.Formatter):
    """Log formatter that includes session and job IDs."""

    def format(self, record):
        session_id = _session_id.get()
        job_id = _job_id.get()

        record.session_id = session_id if session_id else "unknown"
        record.job_id = job_id if job_id else "unknown"

        return super().format(record)


class LoggingSession:
    """Context manager for logging related operations together."""

    def __init__(self, session_id: str, job_id: str = None):
        self.session_id = session_id
        self.job_id = job_id
        self.logger = logging.getLogger(__name__)

    def __enter__(self):
        _session_id.set(self.session_id)
        if self.job_id:
            _job_id.set(self.job_id)

        self.logger.info(f"Starting logging session: {self.session_id}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.logger.error(f"Session {self.session_id} failed: {exc_type.__name__}: {exc_val}")
        else:
            self.logger.info(f"Session {self.session_id} completed successfully")

        _session_id.set(None)
        _job_id.set(None)


def _format_arg(arg, max_length: int = 100) -> str:
    """Format argument for logging (truncate large objects)."""
    if arg is None:
        return "None"
    elif isinstance(arg, str):
        return f'"{arg[:max_length]}..."' if len(arg) > max_length else f'"{arg}"'
    elif isinstance(arg, (int, float, bool)):
        return str(arg)
    elif isinstance(arg, dict):
        keys = list(arg.keys())[:3]
        items = ", ".join(f"{k}=..." for k in keys)
        return f"{{{items}}}"
    elif isinstance(arg, (list, tuple)):
        return f"{type(arg).__name__}[{len(arg)}]"
    else:
        return f"<{type(arg).__name__}>"


def log_execution(include_args: bool = False, include_result: bool = False):
    """Decorator to log function execution with optional args/result logging."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = logging.getLogger(func.__module__)

            arg_str = ""
            if include_args:
                arg_reprs = [_format_arg(a) for a in args]
                arg_reprs.extend([f"{k}={_format_arg(v)}" for k, v in kwargs.items()])
                arg_str = f"({', '.join(arg_reprs)})"

            logger.info(f"Starting {func.__name__}{arg_str}")

            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                elapsed = time.time() - start_time

                result_str = ""
                if include_result:
                    result_str = f" -> {_format_arg(result)}"

                logger.info(f"Completed {func.__name__} in {elapsed:.2f}s{result_str}")
                return result

            except Exception as e:
                elapsed = time.time() - start_time
                logger.error(f"Failed {func.__name__} after {elapsed:.2f}s: {e}", exc_info=True)
                raise

        return wrapper

    if callable(include_args):
        func = include_args
        include_args = False
        return decorator(func)
    return decorator


class PipelineLogger:
    """Configures and provides structured logging for the pipeline."""

    _initialized = False

    @classmethod
    def setup_logging(cls, log_config: Dict[str, Any] = None, log_dir: str = "../logs"):
        if cls._initialized:
            return

        os.makedirs(log_dir, exist_ok=True)
        log_config = log_config or {}

        level_file = getattr(logging, log_config.get("level_file", "INFO"))
        level_console = getattr(logging, log_config.get("level_console", "INFO"))
        format_str = log_config.get(
            "format", "%(asctime)s | %(levelname)-8s | [%(session_id)s] %(name)-20s | %(message)s"
        )

        log_file = os.path.join(log_dir, f"pipeline_{datetime.now().strftime('%Y%m%d')}.log")

        formatter = SessionAwareFormatter(fmt=format_str, datefmt="%Y-%m-%d %H:%M:%S")

        # File Handler with rotation
        if log_config.get("enable_rotation", True):
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=log_config.get("file_max_bytes", 10 * 1024 * 1024),
                backupCount=log_config.get("backup_count", 5),
            )
        else:
            file_handler = logging.FileHandler(log_file)

        file_handler.setFormatter(formatter)
        file_handler.setLevel(level_file)

        # Console Handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(level_console)

        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)

        # Remove existing handlers to avoid duplicates
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)

        cls._initialized = True
        logging.getLogger(__name__).info(f"Logging initialized. Writing to {log_file}")

    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        if not cls._initialized:
            cls.setup_logging()
        return logging.getLogger(name)
