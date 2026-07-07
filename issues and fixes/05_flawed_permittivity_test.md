# Issue 5: Flawed Unit Test for Pydantic Edge Cases

## Description
In `tests/test_edge_cases.py`, the `test_pydantic_validation_edge_cases` function was written to assert that a `material_permittivity` of `0.5` is considered valid.

## Impact
This caused `pytest` to fail because the new backend `InputValidator` in `codes/input_validation.py` correctly rejects permittivity values below `1.0` (which is the permittivity of a vacuum) as physically impossible. 

## Fix Applied
I updated the test in `test_edge_cases.py` to use `1.0` as the minimum valid edge case instead of `0.5`. The test suite now passes successfully.
