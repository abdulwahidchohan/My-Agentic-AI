# agentic_ai_framework/tools/system_tools.py
import subprocess
import platform
import asyncio
from tools import BaseTool
from utils.logger import setup_logger
from pydantic import BaseModel, Field

logger = setup_logger(__name__)

class OpenApplicationArgs(BaseModel):
    app_name: str = Field(..., description="The name of the application to open (e.g., 'Google Chrome', 'Notepad', 'Microsoft Word').")

async def open_application_func(app_name: str) -> str:
    """Opens a specified application on the operating system."""
    logger.info(f"Attempting to open application: {app_name}")
    try:
        await asyncio.sleep(0.5) # Simulate delay
        if platform.system() == "Windows":
            subprocess.Popen([app_name])
        elif platform.system() == "Darwin": # macOS
            subprocess.Popen(["open", "-a", app_name])
        else: # Linux
            subprocess.Popen([app_name.lower()]) # Assuming common linux app names are lowercase
        return f"Successfully attempted to open {app_name}."
    except Exception as e:
        logger.error(f"Error opening application {app_name}: {e}")
        return f"Error opening application: {e}. Check if the application name is correct or if it's in your PATH."

OpenApplicationTool = BaseTool(
    name="open_application",
    description="Opens a specified application on the user's operating system.",
    func=open_application_func,
    schema=OpenApplicationArgs.model_json_schema()
)

class RunCommandArgs(BaseModel):
    command: str = Field(..., description="The shell command to execute.")

async def run_shell_command_func(command: str) -> str:
    """
    Executes a shell command. DANGEROUS! Use with extreme caution and strong user confirmation.
    """
    logger.warning(f"Executing potentially dangerous shell command: '{command}'")
    try:
        await asyncio.sleep(1) # Simulate delay
        process = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        return f"Command executed. STDOUT:\n{process.stdout}\nSTDERR:\n{process.stderr}"
    except subprocess.CalledProcessError as e:
        logger.error(f"Shell command failed with exit code {e.returncode}: {e.stderr}")
        return f"Command failed: {e.stderr}"
    except Exception as e:
        logger.error(f"Error executing shell command '{command}': {e}")
        return f"Error executing command: {e}"

RunShellCommandTool = BaseTool(
    name="run_shell_command",
    description="Executes a shell command on the operating system. USE WITH EXTREME CAUTION.",
    func=run_shell_command_func,
    schema=RunCommandArgs.model_json_schema()
)