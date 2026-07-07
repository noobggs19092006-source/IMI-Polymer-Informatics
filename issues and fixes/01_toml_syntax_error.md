# Issue 1: `pyproject.toml` Syntax Errors

## Description
The project configuration file `pyproject.toml` contained Python-style boolean values (`True`/`False`) instead of TOML standard lowercase booleans (`true`/`false`).

## Impact
This caused configuration parsers (including `pytest` and `black`) to crash immediately upon initialization, preventing the entire test suite and formatting tools from running.

## Fix Applied
I updated lines 3-10, 14, 18, 37, and 38 in `pyproject.toml` to replace all instances of `True` with `true` and `False` with `false`. The configuration is now fully valid TOML.
