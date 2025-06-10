# base_agent.py
# agentic_ai_framework/agents/base_agent.py
import asyncio
from llm_client import LLMClient
from utils.logger import setup_logger
from utils.prompt_formatter import PromptFormatter
from typing import List, Dict, Callable, Any, Union
import inspect
from PIL.Image import Image as PILImage # For type hinting PIL Image objects
import chainlit as cl # For Chainlit integration

logger = setup_logger(__name__)

class BaseAgent:
    def __init__(self, name: str, role: str, goal: str, instructions: str,
                 llm_client: LLMClient, memory=None, tools: List[Any] = None): # tools will be BaseTool instances
        self.name = name
        self.role = role
        self.goal = goal
        self.instructions = instructions
        self.llm_client = llm_client
        self.memory = memory
        self._tools = {tool.name: tool for tool in tools} if tools else {} # Map tool name to tool object

    def add_tool(self, tool: Any): # Expects BaseTool instance
        self._tools[tool.name] = tool
        logger.info(f"Tool '{tool.name}' added to {self.name}.")

    def get_tools(self) -> List[Any]:
        return list(self._tools.values())

    async def _execute_tool_call(self, tool_call: Any) -> Any:
        """
        Executes a tool call requested by the LLM.
        `tool_call` can be a Gemini FunctionCall or OpenAI ToolCall object.
        """
        tool_name = tool_call.function.name
        tool_args = tool_call.function.args.copy() # Make a mutable copy of args

        if tool_name not in self._tools:
            logger.error(f"Agent {self.name} attempted to call unknown tool: {tool_name}")
            return f"Error: Tool '{tool_name}' not found."

        tool_func = self._tools[tool_name].func
        
        async with cl.Step(name=f"Tool: {tool_name}", type="tool", parent_id=cl.get_current_step().id) as tool_step:
            tool_step.input = tool_args # Display tool arguments in Chainlit UI
            logger.info(f"Agent {self.name} calling tool '{tool_name}' with args: {tool_args}")

            try:
                # Check if the tool function is async
                if inspect.iscoroutinefunction(tool_func):
                    tool_output = await tool_func(**tool_args)
                else:
                    tool_output = tool_func(**tool_args)
                tool_step.output = tool_output # Display tool output in Chainlit UI
                logger.info(f"Tool '{tool_name}' returned: {tool_output}")
                return tool_output
            except Exception as e:
                tool_step.output = f"Error executing tool: {e}"
                tool_step.status = cl.StepStatus.FAILED
                logger.error(f"Error executing tool '{tool_name}': {e}")
                return f"Error executing tool '{tool_name}': {e}"

    async def generate_response(self, prompt: str, multimodal_content: List[Union[str, PILImage]] = None, **kwargs) -> str:
        """
        Generates a response using the LLM, potentially with multimodal input and handling tool calls.
        """
        # Build the initial conversation history for the LLM
        history_parts = [{"role": "system", "parts": [self.instructions]}]
        
        user_parts = []
        if multimodal_content:
            for item in multimodal_content:
                if isinstance(item, str):
                    user_parts.append({"text": item})
                elif isinstance(item, PILImage):
                    user_parts.append(item) # PIL Image objects are directly supported by Gemini
        user_parts.append({"text": prompt}) # Add the main text prompt

        history_parts.append({"role": "user", "parts": user_parts})
        
        num_retries = 0
        max_retries = 3 # Prevent infinite tool call loops
        
        while num_retries < max_retries:
            llm_response = await self.llm_client.generate_content(
                contents=history_parts,
                tools=self.get_tools(),
                **kwargs
            )
            
            if isinstance(llm_response, dict) and "tool_calls" in llm_response:
                # If the LLM wants to call tools, execute them
                tool_outputs = []
                for tool_call in llm_response["tool_calls"]:
                    output = await self._execute_tool_call(tool_call)
                    tool_outputs.append({
                        "function_name": tool_call.function.name,
                        "output": output
                    })
                
                # After executing tools, append tool outputs to history and call LLM again
                # Convert tool outputs to a format LLM understands
                tool_output_messages = []
                for tc in tool_outputs:
                    # Gemini expects function call responses in this format
                    tool_output_messages.append(
                        genai.protos.Part(
                            function_response=genai.protos.FunctionResponse(
                                name=tc['function_name'],
                                response=genai.protos.Response(
                                    data=tc['output']
                                )
                            )
                        )
                    )
                
                history_parts.append({"role": "function", "parts": tool_output_messages})
                logger.info(f"Appended tool outputs to history. Retrying LLM call. Retry count: {num_retries + 1}")
                num_retries += 1
            else:
                # LLM generated a text response, not a tool call
                return llm_response
        
        logger.error(f"Agent {self.name} exceeded max tool call retries.")
        return "I tried to use tools multiple times but couldn't get a final answer. Please try clarifying your request."

    async def handle(self, user_input: str, multimodal_content: List[Union[str, PILImage]] = None) -> str:
        """
        Main entry point for an agent to handle a user input.
        """
        raise NotImplementedError(f"Agent '{self.name}' must implement handle method.")