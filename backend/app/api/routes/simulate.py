from fastapi import APIRouter, BackgroundTasks
import subprocess
import structlog
import os

router = APIRouter()
logger = structlog.get_logger(__name__)

def run_simulation_script():
    try:
        # Assuming we are running from the root of the project
        script_path = os.path.join("scripts", "simulator.py")
        subprocess.Popen(["python", script_path])
        logger.info("Simulator script started in background.")
    except Exception as e:
        logger.error(f"Failed to start simulator: {str(e)}")

@router.post("/start")
async def start_simulation(background_tasks: BackgroundTasks):
    """
    Starts the real-time simulator in a separate process.
    """
    background_tasks.add_task(run_simulation_script)
    return {"message": "Simulation started in background."}
