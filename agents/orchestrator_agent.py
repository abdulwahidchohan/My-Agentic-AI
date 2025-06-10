# agentic_ai_framework/agents/orchestrator_agent.py
from .base_agent import BaseAgent
from llm_client import LLMClient
from utils.logger import setup_logger
from typing import Dict, Any, List, Union
from PIL.Image import Image as PILImage # For type hinting PIL Image objects
import chainlit as cl # For Chainlit integration

logger = setup_logger(__name__)

class OrchestratorAgent(BaseAgent):
    def __init__(self, llm_client: LLMClient, agents_map: Dict[str, BaseAgent], memory=None):
        super().__init__(
            name="OrchestratorAgent",
            role="Chief AI Orchestrator and Task Router",
            goal="Understand user intent and intelligently delegate tasks to the most appropriate specialized agent.",
            instructions=(
                "You are the central brain of the AI system. Your primary function is to "
                "interpret user requests and determine which specialized agent (ResearchAgent, "
                "CommunicatorAgent, PlannerAgent, MultimodalInputAgent) is best suited to handle the task. "
                "You should always strive to identify the most relevant agent(s) based on the user's intent. "
                "If multiple agents are needed for a complex task, indicate the primary agent for initial handling or describe a short sequence (e.g., 'research then summarizer')."
                "Respond ONLY with the name of the most suitable agent, exactly as it appears in the list (e.g., 'research', 'communicator', 'planner', 'multimodal_input'). "
                "If you are uncertain or the request is ambiguous, state 'clarify'."
                "Do NOT include any other text or reasoning in your response, just the agent's name."
            ),
            llm_client=llm_client,
            memory=memory
        )
        self.agents_map = agents_map # Reference to all other agents

    async def route_task(self, user_input: str, multimodal_content: List[Union[str, PILImage]] = None) -> str:
        """
        Uses Gemini 1.5 Pro to determine the best agent for the task.
        """
        agent_names = ", ".join(self.agents_map.keys())
        routing_prompt = (
            f"Given the user's request, which of the following specialized agents should handle it?\n"
            f"Available Agents: {agent_names}\n"
            f"User Request: {user_input}\n\n"
            f"Respond ONLY with the name of the most suitable agent (e.g., 'research', 'communicator', 'planner', 'multimodal_input'). "
            f"If uncertain, state 'clarify'."
        )
        
        # Use multimodal input for routing if provided
        response = await self.generate_response(routing_prompt, multimodal_content=multimodal_content)
        
        chosen_agent_name = response.strip().lower().split(' ')[0] # Simple parsing
        
        # Ensure the response is one of the valid agent names or "clarify"
        if chosen_agent_name not in self.agents_map and chosen_agent_name != "clarify":
            logger.warning(f"Orchestrator returned unrecognized agent name: '{chosen_agent_name}'. Defaulting to 'clarify'.")
            chosen_agent_name = "clarify"

        logger.info(f"Orchestrator routed task to: {chosen_agent_name}")
        return chosen_agent_name

    async def handle(self, user_input: str, multimodal_content: List[Union[str, PILImage]] = None) -> str:
        # The OrchestratorAgent primarily handles routing, not direct task execution.
        # Its `handle` method is mainly for internal consistency with BaseAgent.
        logger.info(f"OrchestratorAgent received input for routing: {user_input}")
        return await self.route_task(user_input, multimodal_content)