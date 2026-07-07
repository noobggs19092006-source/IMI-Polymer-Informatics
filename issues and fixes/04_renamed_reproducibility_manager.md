# Issue 4: Missing `ReproducibilityManager` in `tests/run_integration_test.py`

## Description
The integration test `tests/run_integration_test.py` attempted to import `ReproducibilityManager` from `codes.reproducibility`. However, `ReproducibilityManager` was renamed to `DeterministicPipeline` in `codes/reproducibility.py` during the codebase refactoring to version 1.0.0.

## Impact
This caused an `ImportError` that halted test collection, preventing integration tests from running.

## Fix Applied
I replaced the `ReproducibilityManager` import with `DeterministicPipeline` in `tests/run_integration_test.py` and updated all usages of the class to use the new name.
