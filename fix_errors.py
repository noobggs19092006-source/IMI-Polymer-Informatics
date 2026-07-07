import re
import glob

def fix_f541(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'ansys_bridge.py' in file_path:
        content = content.replace('except:', 'except Exception:')
        
    if 'ansys_license_validator.py' in file_path:
        content = content.replace('f"Consider reducing', '"Consider reducing')
        
    if 'code_12_prepare_sweep.py' in file_path:
        content = content.replace('f"--- Initialization Complete', '"--- Initialization Complete')
        
    if 'code_14_inverse_ansys.py' in file_path:
        content = content.replace('f"\\nNo targets achievable', '"\\nNo targets achievable')
        content = content.replace('f"\\nTop 5 Candidates', '"\\nTop 5 Candidates')
        
    if 'code_15_final_report.py' in file_path:
        content = content.replace('p(f"The integration pipeline', 'p("The integration pipeline')
        content = content.replace('p(f"By combining', 'p("By combining')
        
    if 'code_17_pareto_optimization.py' in file_path:
        content = content.replace('f"Optimizing parameters', '"Optimizing parameters')
        content = content.replace('f"--- Pareto Optimization', '"--- Pareto Optimization')
        content = content.replace('f"\\n1. Maximum', '"\\n1. Maximum')
        content = content.replace('f"\\n2. Minimum', '"\\n2. Minimum')
        content = content.replace('f"\\nModel trained', '"\\nModel trained')
        content = content.replace('f"Failed to identify', '"Failed to identify')

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

for f in glob.glob('codes/*.py'):
    fix_f541(f)
