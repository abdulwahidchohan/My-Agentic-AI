# agentic_ai_framework/tools/visual_tools.py
import io
import asyncio
from PIL import Image
from tools import BaseTool
from utils.logger import setup_logger
from pydantic import BaseModel, Field
import mss # For screen capturing
import base64 # For encoding images if needed for non-direct multimodal parts

logger = setup_logger(__name__)

class CaptureScreenArgs(BaseModel):
    monitor: int = Field(1, description="The monitor number to capture (e.g., 1 for primary, 2 for secondary).")

async def capture_screen_func(monitor: int = 1) -> str:
    """
    Captures a screenshot of a specified monitor and returns its content as a base64 string.
    This image can then be fed to Gemini 1.5 Pro's multimodal input.
    """
    logger.info(f"Capturing screen for monitor {monitor}...")
    try:
        await asyncio.sleep(1) # Simulate delay
        with mss.mss() as sct:
            monitor_info = sct.monitors[monitor]
            sct_img = sct.grab(monitor_info)
            img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")

            byte_arr = io.BytesIO()
            img.save(byte_arr, format='PNG')
            encoded_image = base64.b64encode(byte_arr.getvalue()).decode('utf-8')
            logger.info("Screenshot captured and base64 encoded.")
            return encoded_image # This can be used as a part in multimodal input

    except Exception as e:
        logger.error(f"Error capturing screen: {e}")
        return f"Error capturing screen: {e}"

CaptureScreenTool = BaseTool(
    name="capture_screen",
    description="Captures a screenshot of the specified monitor. Returns a base64 encoded image string.",
    func=capture_screen_func,
    schema=CaptureScreenArgs.model_json_schema()
)