# Issue 2: Broken Python Import Paths During Testing

## Description
The test suite in the `tests/` directory imports modules from the `codes/` directory (e.g., `from codes.config_manager import ...`). However, the scripts inside `codes/` use relative-like imports for each other (e.g., `from logger_setup import ...` instead of `from .logger_setup import ...`).

## Impact
Running `pytest tests/` from the root directory failed instantly with `ModuleNotFoundError: No module named 'logger_setup'`. The testing framework couldn't resolve internal imports inside the `codes` package because `codes` was not explicitly added to `sys.path`.

## Fix Applied
Created a `conftest.py` file in the root directory that automatically adds the `codes/` folder to the `sys.path` when `pytest` initializes. This guarantees all internal references like `import logger_setup` correctly resolve to `codes/logger_setup.py` without requiring a massive refactoring of all 34 python files in the `codes/` directory.
