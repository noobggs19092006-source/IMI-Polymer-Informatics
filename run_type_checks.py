import subprocess
import sys

def check_types():
    print("Running type checks using mypy...")
    try:
        import mypy
    except ImportError:
        print("mypy is not installed. Please install it using 'pip install mypy'")
        sys.exit(0)
        
    result = subprocess.run([sys.executable, "-m", "mypy", "codes/"], capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print("Type checking failed.")
        sys.exit(1)
    else:
        print("Type checking passed successfully.")
        sys.exit(0)

if __name__ == "__main__":
    check_types()
