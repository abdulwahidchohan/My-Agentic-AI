# __init__.py
# agentic_ai_framework/tools/__init__.py
import google.generativeai as genai
from typing import Callable, Dict, Any

# Base class for tools, allowing LLMs to understand them for function calling
class BaseTool:
    def __init__(self, name: str, description: str, func: Callable, schema: Dict[str, Any]):
        self.name = name
        self.description = description
        self.func = func
        self.schema = schema

    def to_gemini_format(self):
        """Converts tool definition to Gemini's FunctionDeclaration format."""
        return genai.protos.Tool(
            function_declarations=[
                genai.protos.FunctionDeclaration(
                    name=self.name,
                    description=self.description,
                    parameters=genai.protos.Schema(**self.schema)
                )
            ]
        )

    def to_openai_format(self):
        """Converts tool definition to OpenAI's function schema format."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.schema
            }
        }

# Import all specific tools so they can be easily accessed
from .email_tools import *
from .file_tools import *
from .web_tools import *
from .voice_tools import *
from .system_tools import *
from .visual_tools import *