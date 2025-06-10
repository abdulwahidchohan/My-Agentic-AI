# main.py
# agentic_ai_framework/app.py
import chainlit as cl
import asyncio
from orchestrator import Orchestrator
from utils.logger import setup_logger
from PIL import Image # Needed for Chainlit's cl.Image element content
import base64
import io

logger = setup_logger(__name__)

# Initialize your orchestrator globally (only once when the app starts)
orchestrator = Orchestrator()
logger.info("Chainlit app started. Orchestrator initialized.")

@cl.on_chat_start
async def start():
    """
    This function runs once when a new chat session begins.
    It can be used to set up initial messages or user session variables.
    """
    # Store orchestrator in session if you need a separate instance per user (less common for a single system)
    # cl.user_session.set("orchestrator", Orchestrator())
    
    await cl.Message(content="[Agentic AI]: System Ready. How can I assist you today?").send()
    logger.info("New Chainlit chat session started and welcome message sent.")

@cl.on_message
async def main(message: cl.Message):
    """
    This function runs every time the user sends a message in the Chainlit UI.
    It captures text and potentially multimodal inputs, then delegates to the Orchestrator.
    """
    # Retrieve the globally initialized orchestrator
    # current_orchestrator: Orchestrator = cl.user_session.get("orchestrator")
    current_orchestrator = orchestrator # Using the global instance

    user_text_input = message.content
    user_audio_data = None
    user_image_data = None
    user_video_frame = None

    # Handle file uploads (if enabled in .chainlit/config.toml)
    if message.elements:
        for element in message.elements:
            if isinstance(element, cl.Image):
                # Chainlit cl.Image.content is bytes. Pass directly to agent
                user_image_data = element.content
                await cl.Message(content=f"Received image: **{element.name}**").send()
                logger.info(f"Chainlit received an image: {element.name}")
            elif isinstance(element, cl.Audio):
                user_audio_data = element.content
                await cl.Message(content=f"Received audio: **{element.name}**").send()
                logger.info(f"Chainlit received audio: {element.name}")
            elif isinstance(element, cl.Video):
                user_video_frame = element.content # Assuming this is a single frame or raw video bytes
                await cl.Message(content=f"Received video: **{element.name}**").send()
                logger.info(f"Chainlit received video: {element.name}")
            # Add handling for other file types if needed

    # Delegate the full request (text + multimodal) to the Orchestrator
    final_ai_response = await current_orchestrator.handle_user_request(
        user_text_input=user_text_input,
        user_audio_data=user_audio_data,
        user_image_data=user_image_data,
        user_video_frame=user_video_frame
    )
    
    # Send the final response back to the user in the Chainlit UI
    await cl.Message(content=final_ai_response).send()
    logger.info("Final AI response sent to Chainlit UI.")