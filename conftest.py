import sys
import os

# Add the codes directory to the Python path so tests can run
# from the root of the project using pytest without ImportErrors.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'codes')))
