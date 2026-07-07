"""
Master Orchestrator Script for the Polymer Informatics Pipeline.
This script runs the entire end-to-end pipeline interactively.
"""
import subprocess
import sys
import os
import time
import logging
from codes.logger_setup import PipelineLogger

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(message)s")

def print_header(title):
    logger.info("\n" + "=" * 80)
    logger.info("  %s", title)
    logger.info("=" * 80)

def run_command(command, description):
    logger.info("\n🚀 Starting: %s", description)
    logger.info("💻 Command:  %s", ' '.join(command))
    logger.info("-" * 80)
    
    # Use subprocess.Popen to stream the output interactively
    try:
        process = subprocess.Popen(
            command,
            stdout=sys.stdout,
            stderr=sys.stderr,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        process.wait()
        
        if process.returncode != 0:
            logger.error("\n❌ Error: Step failed with exit code %d", process.returncode)
            return False
        else:
            logger.info("\n✅ Successfully completed: %s", description)
        return True
    except KeyboardInterrupt:
        logger.warning("\n⚠️ Process interrupted by user.")
        return False
    except Exception as e:
        logger.error("\n❌ Failed to run command: %s", e)
        return False

def main():
    print_header("PHYSICS-INFORMED POLYMER INFORMATICS & DIGITAL TWIN PIPELINE")
    logger.info("This script will guide you through the execution of the entire pipeline.")
    
    pipeline_steps = [
        # Phase 1
        (["python", "codes/code_12_ansys_check.py"], "1. ANSYS Connection Check"),
        (["python", "codes/data_pipeline.py"], "2. Physical Baseline Data Generation"),
        (["python", "codes/code_12_prepare_sweep.py"], "3. Combinatorial Target Generation"),
        
        # Phase 2
        (["python", "codes/code_12_ansys_sweep.py"], "4. ANSYS Maxwell 2D Sweep (WARNING: Takes hours. Auto-resumes if stopped)"),
        (["python", "codes/rank_successful_polymers.py"], "5. Simulation Ranking & Post-Processing"),
        
        # Phase 3
        (["python", "codes/code_13_train_ansys.py"], "6. Surrogate Ensemble Training"),
        (["python", "codes/code_18_gnn_training.py"], "7. Message Passing Neural Network (GNN) Training"),
        
        # Phase 4
        (["python", "codes/code_14_inverse_ansys.py"], "8. Multi-Objective Inverse Optimization"),
        (["python", "codes/code_17_pareto_optimization.py"], "9. Pareto Frontier Analysis"),
        (["python", "codes/code_19_vae_discovery.py"], "10. Generative VAE Polymer Discovery"),
        
        # Phase 5
        (["python", "codes/code_15_final_report.py"], "11. Academic Report Generation")
    ]
    
    run_all = False
    
    for command, description in pipeline_steps:
        if not run_all:
            logger.info("\nNext Step: %s", description)
            choice = input("Do you want to run this step? [y=yes, n=skip, a=run all remaining, q=quit]: ").strip().lower()
            
            if choice == 'q':
                logger.info("Exiting pipeline orchestrator.")
                sys.exit(0)
            elif choice == 'n':
                logger.info("Skipping: %s", description)
                continue
            elif choice == 'a':
                run_all = True
        
        success = run_command(command, description)
        if not success:
            choice = input("\nStep failed or was interrupted. Do you want to continue to the next step? [y/n]: ").strip().lower()
            if choice.lower() != 'y':
                logger.error("Exiting pipeline orchestrator due to failure.")
                sys.exit(1)
                
    print_header("PIPELINE PROCESSING COMPLETE")
    
    logger.info("\nNext, you can launch the interactive applications (these run continuously).")
    
    dashboard_choice = input("Do you want to launch the Streamlit Dashboard? [y/n]: ").strip().lower()
    if dashboard_choice == 'y':
        logger.info("\nStarting Streamlit Dashboard... (Press Ctrl+C to stop)")
        try:
            subprocess.run(["streamlit", "run", "codes/code_16_dashboard.py"])
        except KeyboardInterrupt:
            pass
        
    api_choice = input("\nDo you want to launch the FastAPI backend? [y/n]: ").strip().lower()
    if api_choice == 'y':
        logger.info("\nStarting FastAPI Server... (Press Ctrl+C to stop)")
        try:
            subprocess.run(["uvicorn", "codes.backend_api:app", "--reload"])
        except KeyboardInterrupt:
            pass
        
    logger.info("\nThank you for using the Polymer Informatics Pipeline!")

if __name__ == "__main__":
    # Ensure we run from the project root
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    main()
