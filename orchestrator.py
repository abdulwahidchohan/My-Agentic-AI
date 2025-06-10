# orchestrator.py
# agentic_ai_framework/orchestrator.py
import asyncio
from llm_client import LLMClient
from memory.memory_store import MemoryStore
from memory.rag_module import RAGModule
from agents import OrchestratorAgent, ResearchAgent, CommunicatorAgent, PlannerAgent, MultimodalInputAgent, BaseAgent
from tools import WebSearchTool, SendEmailTool, ReadEmailTool, ReadFileTool, WriteFileTool, ListDirectoryTool, \
                  TextToSpeechTool, SpeechToTextTool, OpenApplicationTool, RunShellCommandTool, CaptureScreenTool
from utils.logger import setup_logger
from typing import Dict, Any, List, Union
from PIL.Image import Image as PILImage # For type hinting PIL Image objects
import chainlit as cl # For Chainlit integration

logger = setup_logger(__name__)

class Orchestrator:
    def __init__(self):
        logger.info("Initializing Orchestrator...")
        self.llm_client = LLMClient()
        self.memory_store = MemoryStore()
        self.rag_module = RAGModule(self.memory_store)

        # Initialize specialized agents
        # Pass all potential tools to agents that might use them.
        # The BaseAgent's generate_response method will ensure LLM uses only relevant tools.
        common_tools = [WebSearchTool, SendEmailTool, ReadEmailTool, ReadFileTool, WriteFileTool, ListDirectoryTool, 
                        TextToSpeechTool, SpeechToTextTool, OpenApplicationTool, RunShellCommandTool, CaptureScreenTool]

        self.research_agent = ResearchAgent(llm_client=self.llm_client, memory_rag=self.rag_module)
        self.communicator_agent = CommunicatorAgent(llm_client=self.llm_client, memory=self.rag_module)
        self.planner_agent = PlannerAgent(llm_client=self.llm_client, memory=self.rag_module)
        self.multimodal_input_agent = MultimodalInputAgent(llm_client=self.llm_client)

        # You might want to assign specific tools to specific agents if they only need a subset
        # For this comprehensive example, BaseAgent gets all tools it might need.
        for tool in common_tools:
            self.research_agent.add_tool(tool)
            self.communicator_agent.add_tool(tool)
            self.planner_agent.add_tool(tool)
            # MultimodalInputAgent does not directly use external tools in its handle method,
            # but relies on LLM's multimodal processing.

        # Map agent names to instances for the OrchestratorAgent
        self.agents_map: Dict[str, BaseAgent] = {
            "research": self.research_agent,
            "communicator": self.communicator_agent,
            "planner": self.planner_agent,
            "multimodal_input": self.multimodal_input_agent # Orchestrator can route to this first
        }
        
        # The main orchestrator agent that routes tasks
        self.orchestrator_agent = OrchestratorAgent(
            llm_client=self.llm_client,
            agents_map=self.agents_map,
            memory=self.rag_module # Orchestrator also benefits from memory
        )
        logger.info("All agents initialized.")

    async def _process_multimodal_input(self, text_input: str = None, audio_input: bytes = None, image_input: bytes = None, video_frame_input: bytes = None) -> Dict[str, Union[str, List[Any]]]:
        """
        Helper to delegate raw multimodal inputs to the MultimodalInputAgent.
        """
        if audio_input or image_input or video_frame_input:
            logger.info("Detected raw multimodal input. Routing to MultimodalInputAgent for initial parsing.")
            parsed_data = await self.multimodal_input_agent.handle(
                audio_data=audio_input,
                image_data=image_input,
                video_frame_data=video_frame_input,
                text_input=text_input # Pass along any initial text input
            )
            return parsed_data
        else:
            # If no raw multimodal data, just return the text input
            return {"parsed_text": text_input, "multimodal_parts": [text_input] if text_input else []}

    async def handle_user_request(self, user_text_input: str, user_audio_data: bytes = None, user_image_data: bytes = None, user_video_frame: bytes = None) -> str:
        """
        Processes a full user request, including multimodal inputs, routes it, and executes the task.
        """
        # Step 1: Process raw multimodal inputs via MultimodalInputAgent
        processed_input = await self._process_multimodal_input(
            text_input=user_text_input,
            audio_input=user_audio_data,
            image_input=user_image_data,
            video_frame_input=user_video_frame
        )
        
        cleaned_input_text = processed_input["parsed_text"]
        multimodal_context_parts = processed_input["multimodal_parts"]

        if not cleaned_input_text.strip():
            return "Please provide some input (text, audio, or image)."

        logger.info(f"Received processed input: {cleaned_input_text} (Multimodal parts count: {len(multimodal_context_parts)})")
        
        # Step 2: OrchestratorAgent routes the task
        async with cl.Step(name="Orchestrator Routing", type="llm") as route_step:
            route_step.input = cleaned_input_text # Show the text input to orchestrator
            chosen_agent_name = await self.orchestrator_agent.route_task(
                cleaned_input_text, multimodal_content=multimodal_context_parts
            )
            route_step.output = f"Routed to: {chosen_agent_name}"
            await cl.Message(content=f"AI: Routing to **{chosen_agent_name}** agent...").send()

        if chosen_agent_name == "clarify":
            return "I'm not sure how to handle that. Can you please clarify your request?"
        
        target_agent = self.agents_map.get(chosen_agent_name)
        if not target_agent:
            logger.error(f"Orchestrator routed to non-existent agent: {chosen_agent_name}")
            return f"I've identified an agent for this, but it seems **{chosen_agent_name}** is not available. Please check system configuration."

        # Step 3: Delegate and execute the task
        logger.info(f"Delegating task to {target_agent.name}...")
        
        try:
            async with cl.Step(name=f"Agent: {target_agent.name} Execution", type="agent") as agent_exec_step:
                agent_exec_step.input = cleaned_input_text # Show the text input to agent
                final_output = await target_agent.handle(
                    cleaned_input_text, multimodal_content=multimodal_context_parts
                )
                agent_exec_step.output = f"Agent completed. Output: {final_output[:200]}..."

            # Step 4: Optionally add the interaction to long-term memory
            await self.memory_store.add_to_memory(
                text=f"User Query: {cleaned_input_text}\nAI Response: {final_output}",
                metadata={"agent": target_agent.name, "timestamp": asyncio.current_task()._loop.time()}
            )
            return final_output

        except NotImplementedError:
            logger.error(f"Agent {target_agent.name} has not implemented its handle method.")
            return f"**{target_agent.name}** is not fully implemented yet for this type of task."
        except Exception as e:
            logger.error(f"An error occurred while executing task with {target_agent.name}: {e}", exc_info=True)
            return f"An error occurred while processing your request with **{target_agent.name}**. Please check logs for details."