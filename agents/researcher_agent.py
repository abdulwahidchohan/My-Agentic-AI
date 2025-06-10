# researcher_agent.py
# agentic_ai_framework/agents/researcher_agent.py
from .base_agent import BaseAgent
from llm_client import LLMClient
from tools import WebSearchTool # Import the tool
from memory.rag_module import RAGModule # For internal knowledge search
from utils.logger import setup_logger
from typing import List, Union
from PIL.Image import Image as PILImage # For type hinting PIL Image objects
import chainlit as cl # For Chainlit integration

logger = setup_logger(__name__)

class ResearcherAgent(BaseAgent):
    def __init__(self, llm_client: LLMClient, memory_rag: RAGModule):
        super().__init__(
            name="ResearchAgent",
            role="Expert Research Assistant",
            goal="Gather comprehensive and factual information from web searches and internal knowledge bases.",
            instructions=(
                "You are an expert researcher. Your primary goal is to find accurate and relevant information. "
                "Always use your `serper_search` tool for external web queries when new information is needed. "
                "For internal knowledge, use your RAG capabilities (implied through memory context). "
                "Synthesize findings clearly and cite sources where appropriate. "
                "If a query is ambiguous, ask for clarification. Prioritize factual and up-to-date information."
            ),
            llm_client=llm_client,
            memory=memory_rag,
            tools=[WebSearchTool] # Assign web search tool
        )
        self.rag_module = memory_rag

    async def handle(self, user_input: str, multimodal_content: List[Union[str, PILImage]] = None) -> str:
        logger.info(f"[ResearchAgent] Handling research task for: {user_input}")

        async with cl.Step(name="RAG Query", type="retrieval", parent_id=cl.get_current_step().id) as rag_step:
            relevant_docs = await self.rag_module.query_memory(user_input)
            if relevant_docs:
                internal_context = "Relevant internal knowledge:\n" + "\n".join([f"- {doc}" for doc in relevant_docs])
                rag_step.output = f"Found {len(relevant_docs)} relevant internal documents."
                logger.info("[ResearchAgent] Found relevant internal knowledge.")
                # Augment the prompt with internal context
                prompt_with_context = f"{user_input}\n\n{internal_context}\n\nConsider this context, but also perform a web search if necessary to get the latest information."
            else:
                prompt_with_context = user_input
                rag_step.output = "No relevant internal documents found."
                logger.info("[ResearchAgent] No relevant internal knowledge, proceeding with potential web search.")
        
        async with cl.Step(name="LLM Research & Tool Use", type="llm", parent_id=cl.get_current_step().id) as llm_step:
            # Let Gemini decide to use the web search tool based on the prompt_with_context
            result = await self.generate_response(prompt_with_context, multimodal_content=multimodal_content)
            llm_step.output = f"LLM generated response: {result[:200]}..."

        # After getting result, you might want to store new insights in memory
        if self.memory:
            await self.memory.add_to_memory(user_input, result) # Store query and result for future RAG

        return result