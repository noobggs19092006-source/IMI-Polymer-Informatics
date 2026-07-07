# Issue 6: Ansys Stability Regression (Hard-Closing Desktop)

## Description
In `codes/resource_manager.py`, the `managed_ansys_job` context manager was calling `m2d_instance.release_desktop(True, True)`.

## Impact
Calling `release_desktop(True, True)` forces the Ansys desktop and all active projects to close. In a batch simulation or live inference environment, restarting the massive Ansys Desktop GUI for every single simulation adds 20-30 seconds of overhead and frequently causes gRPC crashes or freezes when rapidly opening and closing. This essentially re-introduced the Ansys crashing bug that we fixed earlier.

## Fix Applied
I updated the context manager to call `release_desktop(False, False)`. This ensures that the gRPC connection is cleanly released (preventing dangling pointer memory leaks), but leaves the Ansys Desktop running in the background for rapid, subsequent simulations.
