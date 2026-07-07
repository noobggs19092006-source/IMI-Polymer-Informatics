import os
from ansys.aedt.core import Desktop
import sys

# Force UTF-8 for print statements in Windows
sys.stdout.reconfigure(encoding='utf-8')

project_path = os.path.join(os.getcwd(), "Ansys_Connection_Test.aedt")

try:
    # Simplified call for the new ansys-aedt-core 0.27.1
    d = Desktop(version="2025.2", non_graphical=False, student_version=True)
    
    print("✅ Success! Python successfully launched ANSYS Electronics Desktop 2025 R2.")
    print(f"Current AEDT Version: {d.aedt_version_id}")
    
    # Close the session safely
    d.release_desktop(True, True)
    print("Session closed safely.")

except Exception as e:
    print("Error: Could not connect to ANSYS.")
    print(f"Details: {str(e)}")
    print("\nPlease verify that ANSYS is installed correctly and environment variables are set.")
