# agentic_ai_framework/llm_client.py
import google.generativeai as genai
from openai import OpenAI as OpenAIClient # Alias to avoid conflict with `openai-agents` module if used
from config import GEMINI_API_KEY, OPENAI_API_KEY, MODEL_SETTINGS, GEMINI_API_BASE, OPENAI_API_BASE
from utils.logger import setup_logger
from typing import List, Dict, Any, Union
from PIL.Image import Image as PILImage # For type hinting PIL Image objects
import asyncio

logger = setup_logger(__name__)

class LLMClient:
    def __init__(self, model_name: str = None):
        self.gemini_model_name = model_name or MODEL_SETTINGS["gemini_model"]
        self.openai_model_name = model_name or MODEL_SETTINGS["openai_model"]
        self.temperature = MODEL_SETTINGS["temperature"]
        self.max_tokens = MODEL_SETTINGS["max_tokens"]

        if GEMINI_API_KEY:
            genai.configure(api_key=GEMINI_API_KEY)
            self.gemini_client = genai.GenerativeModel(self.gemini_model_name)
            logger.info(f"Initialized Gemini client with model: {self.gemini_model_name}")
        else:
            self.gemini_client = None
            logger.warning("GEMINI_API_KEY not found. Gemini client not initialized.")

        if OPENAI_API_KEY:
            self.openai_client = OpenAIClient(api_key=OPENAI_API_KEY, base_url=OPENAI_API_BASE)
            logger.info(f"Initialized OpenAI client with model: {self.openai_model_name}")
        else:
            self.openai_client = None
            logger.warning("OPENAI_API_KEY not found. OpenAI client not initialized.")

    async def generate_content(self, contents: List[Union[str, PILImage, Dict]], tools: list = None, use_gemini: bool = True, **kwargs) -> Union[str, Dict]:
        """
        Generates content (text or tool calls) using the specified LLM.
        `contents` can be a list of strings, PIL.Image.Image objects, or dicts for roles.
        Returns a string response or a dict with 'tool_calls' if the LLM wants to call tools.
        """
        if use_gemini:
            if not self.gemini_client:
                logger.error("Gemini client not available.")
                return "Error: Gemini client not configured."
            
            gemini_parts = []
            for item in contents:
                if isinstance(item, str):
                    gemini_parts.append({"text": item})
                elif isinstance(item, PILImage):
                    gemini_parts.append(item) # PIL Image objects are directly supported
                elif isinstance(item, dict):
                    gemini_parts.append(item) # For system/user/function roles

            gemini_tools = [tool.to_gemini_format() for tool in tools if hasattr(tool, 'to_gemini_format')] if tools else None

            try:
                response = await self.gemini_client.generate_content_async(
                    contents=gemini_parts,
                    generation_config={
                        "temperature": kwargs.get("temperature", self.temperature),
                        "max_output_tokens": kwargs.get("max_tokens", self.max_tokens),
                    },
                    tools=gemini_tools if gemini_tools else None
                )
                if response.candidates and response.candidates[0].function_calls:
                    tool_calls = response.candidates[0].function_calls
                    return {"tool_calls": tool_calls}
                return response.text
            except Exception as e:
                logger.error(f"Error calling Gemini API: {e}")
                return f"Error: {e}"
        else: # Use OpenAI client
            if not self.openai_client:
                logger.error("OpenAI client not available.")
                return "Error: OpenAI client not configured."
            
            messages = []
            for item in contents:
                if isinstance(item, str):
                    messages.append({"role": "user", "content": item})
                elif isinstance(item, dict) and 'role' in item and 'parts' in item:
                    # Assuming dictionary format like {"role": "system", "parts": ["instruction"]}
                    # Need to convert to OpenAI chat completion message format
                    content_str = "\n".join([part['text'] if isinstance(part, dict) and 'text' in part else str(part) for part in item['parts']])
                    messages.append({"role": item['role'], "content": content_str})
                elif isinstance(item, PILImage):
                    logger.warning("OpenAI client does not directly support PIL.Image.Image for input without conversion.")
                    messages.append({"role": "user", "content": "An image was provided but could not be processed by OpenAI client directly."})


            openai_tools = [tool.to_openai_format() for tool in tools if hasattr(tool, 'to_openai_format')] if tools else None

            try:
                response = await self.openai_client.chat.completions.create(
                    model=kwargs.get("model", self.openai_model_name),
                    messages=messages,
                    temperature=kwargs.get("temperature", self.temperature),
                    max_tokens=kwargs.get("max_tokens", self.max_tokens),
                    tools=openai_tools if openai_tools else None
                )
                if response.choices[0].message.tool_calls:
                    tool_calls = response.choices[0].message.tool_calls
                    return {"tool_calls": tool_calls}
                return response.choices[0].message.content
            except Exception as e:
                logger.error(f"Error calling OpenAI API: {e}")
                return f"Error: {e}"