# prompt_formatter.py
# agentic_ai_framework/utils/prompt_formatter.py

class PromptFormatter:
    @staticmethod
    def format_agent_instruction(role: str, goal: str, capabilities: list, constraints: list) -> str:
        """Formats a system instruction for an agent."""
        instruction = f"You are a {role}. Your main goal is to {goal}.\n"
        if capabilities:
            instruction += "Your capabilities include:\n" + "\n".join([f"- {cap}" for cap in capabilities]) + "\n"
        if constraints:
            instruction += "You must adhere to the following constraints:\n" + "\n".join([f"- {con}" for con in constraints]) + "\n"
        return instruction

    @staticmethod
    def format_tool_description(tool_name: str, tool_description: str, tool_schema: dict) -> str:
        """Formats a description for an LLM to understand a tool (for internal use if needed)."""
        return (
            f"Tool Name: {tool_name}\n"
            f"Description: {tool_description}\n"
            f"Schema: {tool_schema}\n"
            "Use this tool when relevant to your task."
        )

    @staticmethod
    def format_user_query(query: str, context: str = None) -> str:
        """Formats a user query, optionally with additional context."""
        formatted_query = f"User Query: {query}"
        if context:
            formatted_query += f"\nRelevant Context: {context}"
        return formatted_query