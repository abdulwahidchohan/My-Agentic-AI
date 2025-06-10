# agentic_ai_framework/agents/multimodal_input_agent.py
from .base_agent import BaseAgent
from llm_client import LLMClient
from utils.logger import setup_logger
from PIL import Image # For handling PIL Image objects
from typing import List, Union, Dict, Any
import io
import base64
import asyncio
import chainlit as cl # For Chainlit integration

logger = setup_logger(__name__)

class MultimodalInputAgent(BaseAgent):
    def __init__(self, llm_client: LLMClient):
        super().__init__(
            name="MultimodalInputAgent",
            role="Multimodal Input Processor and Interpreter",
            goal="Convert raw multimodal inputs (voice, image/video frames) into structured information and clear textual prompts for other agents.",
            instructions=(
                "You are the gateway for multimodal input. Your task is to accurately transcribe audio, "
                "interpret visual information from images/video frames, and extract key context from "
                "these inputs. Your output should be a clear, concise textual prompt that captures the "
                "user's intent and any relevant visual context, ready for the OrchestratorAgent or other specialized agents. "
                "If provided with an image or video frame, describe its key elements and any text content. "
                "If it's primarily a visual request (e.g., 'what's in this image?'), describe the image first. "
                "If audio, transcribe the audio."
            ),
            llm_client=llm_client
            # No specific tools directly here; its "tools" are internal processing steps/LLM multimodal capabilities
        )

    async def handle(self, audio_data: bytes = None, image_data: bytes = None, video_frame_data: bytes = None, text_input: str = None) -> Dict[str, Union[str, List[Union[str, Image]]]]:
        """
        Processes raw multimodal inputs.
        Returns parsed text and a list of multimodal parts (strings or PIL.Image.Image objects)
        that can be fed to Gemini 1.5 Pro.
        """
        logger.info("[MultimodalInputAgent] Processing multimodal input.")
        
        # This list will hold the various "parts" to send to Gemini
        gemini_input_parts: List[Union[str, Image.Image]] = []
        
        processing_summary = []

        if audio_data:
            async with cl.Step(name="Speech-to-Text", type="tool", parent_id=cl.get_current_step().id) as stt_step:
                # In a real system, send audio_data to a real-time STT service or use your SpeechToTextTool
                # For this example, we'll use a mock or the simulated tool.
                from tools import SpeechToTextTool
                # Create a temporary file to simulate audio_file_path for the tool
                temp_audio_path = "temp_audio.mp3"
                try:
                    with open(temp_audio_path, "wb") as f:
                        f.write(audio_data)
                    transcribed_text = await SpeechToTextTool.func(audio_file_path=temp_audio_path)
                    stt_step.output = f"Transcribed: {transcribed_text}"
                    logger.info(f"Transcribed Audio: {transcribed_text}")
                    gemini_input_parts.append(f"User said: '{transcribed_text}'")
                    processing_summary.append(f"Audio Transcribed: '{transcribed_text}'")
                except Exception as e:
                    stt_step.output = f"Error transcribing audio: {e}"
                    logger.error(f"Error transcribing audio: {e}")
                    gemini_input_parts.append("Error processing audio.")
                finally:
                    if os.path.exists(temp_audio_path):
                        os.remove(temp_audio_path)

        if image_data:
            async with cl.Step(name="Image Processing", type="tool", parent_id=cl.get_current_step().id) as image_step:
                try:
                    img = Image.open(io.BytesIO(image_data))
                    gemini_input_parts.append(img) # Directly append PIL Image
                    image_step.output = "Image processed successfully."
                    processing_summary.append("Image received and processed.")
                except Exception as e:
                    image_step.output = f"Error processing image: {e}"
                    logger.error(f"Failed to process image data: {e}")
                    gemini_input_parts.append("Error processing image.")
        
        if video_frame_data:
            async with cl.Step(name="Video Frame Processing", type="tool", parent_id=cl.get_current_step().id) as video_step:
                try:
                    frame_img = Image.open(io.BytesIO(video_frame_data))
                    gemini_input_parts.append(frame_img) # Directly append PIL Image
                    video_step.output = "Video frame processed successfully."
                    processing_summary.append("Video frame received and processed.")
                except Exception as e:
                    video_step.output = f"Error processing video frame: {e}"
                    logger.error(f"Failed to process video frame data: {e}")
                    gemini_input_parts.append("Error processing video frame.")
        
        if text_input:
            gemini_input_parts.append(f"User's additional text: '{text_input}'")
            processing_summary.append(f"Additional Text: '{text_input}'")

        if not gemini_input_parts:
            logger.warning("MultimodalInputAgent received no valid input data.")
            return {"parsed_text": "No input received.", "multimodal_parts": []}
        
        # Use Gemini 1.5 Pro's multimodal capabilities to understand the combined input
        # Ask Gemini to summarize the intent and describe visual/audio elements.
        final_prompt_for_gemini = (
            f"Based on the provided inputs (which may include text, images, or audio transcripts), "
            f"what is the user's primary intent or request? "
            f"Describe any relevant visual content from images/video frames. "
            f"Extract key context and formulate a clear, actionable textual prompt for another agent. "
            f"Summarize the overall request. Your output should be a single coherent textual representation of the user's full request."
        )

        gemini_input_parts.append(final_prompt_for_gemini) # Add the final instruction

        async with cl.Step(name="Gemini Multimodal Interpretation", type="llm", parent_id=cl.get_current_step().id) as llm_step:
            # The LLM will process the `gemini_input_parts` list, which can contain both text and images/video frames.
            llm_response = await self.llm_client.generate_content(contents=gemini_input_parts)
            parsed_text_from_multimodal = llm_response # This will be Gemini's interpretation
            llm_step.output = f"Gemini's interpretation: {parsed_text_from_multimodal[:200]}..."
            logger.info(f"Multimodal input parsed to: {parsed_text_from_multimodal}")

        return {"parsed_text": parsed_text_from_multimodal, "multimodal_parts": gemini_input_parts}