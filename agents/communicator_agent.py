# communicator_agent.py
# agentic_ai_framework/agents/communicator_agent.py
from .base_agent import BaseAgent
from llm_client import LLMClient
from tools import SendEmailTool, ReadEmailTool # Import relevant tools
from utils.logger import setup_logger
from typing import List, Union
from PIL.Image import Image as PILImage # For type hinting PIL Image objects
import chainlit as cl # For Chainlit integration

logger = setup_logger(__name__)

class CommunicatorAgent(BaseAgent):
    def __init__(self, llm_client: LLMClient, memory=None):
        super().__init__(
            name="CommunicatorAgent",
            role="Professional Communication Manager",
            goal="Draft, send, and manage emails, schedule meetings, and handle digital messages.",
            instructions=(
                "You are a skilled communicator. Use your `send_email` and `read_email` tools to manage communications. "
                "Always confirm with the user before sending sensitive emails. "
                "Draft clear, concise, and polite messages. Be mindful of professional etiquette."
            ),
            llm_client=llm_client,
            memory=memory,
            tools=[SendEmailTool, ReadEmailTool] # Assign communication tools
        )

    async def handle(self, user_input: str, multimodal_content: List[Union[str, PILImage]] = None) -> str:
        logger.info(f"[CommunicatorAgent] Handling communication task for: {user_input}")
        
        async with cl.Step(name="LLM Communication Plan", type="llm", parent_id=cl.get_current_step().id) as step:
            # The prompt will guide Gemini 1.5 Pro to use the appropriate email tool
            response = await self.generate_response(user_input, multimodal_content=multimodal_content)
            step.output = f"Communication plan: {response[:200]}..."
        
        # After Gemini responds (possibly with tool call or text), return the final response
        return response