# planner_agent.py
# agentic_ai_framework/agents/planner_agent.py
from .base_agent import BaseAgent
from llm_client import LLMClient
from tools import BaseTool # You'd define tools like ScheduleEventTool, SetReminderTool
from utils.logger import setup_logger
from typing import List, Union
from PIL.Image import Image as PILImage # For type hinting PIL Image objects
import chainlit as cl # For Chainlit integration
import asyncio

logger = setup_logger(__name__)

# Placeholder for actual planning tools
class ScheduleEventArgs(BaseModel):
    event_name: str = Field(..., description="The name or title of the event.")
    start_time: str = Field(..., description="The start date and time of the event (e.g., '2025-06-15 10:00 AM').")
    end_time: str = Field(..., description="The end date and time of the event.")
    attendees: List[str] = Field(None, description="Optional list of attendee email addresses.")
    location: str = Field(None, description="Optional location for the event.")

async def schedule_event_func(event_name: str, start_time: str, end_time: str, attendees: List[str] = None, location: str = None) -> str:
    """Simulates scheduling an event on a calendar."""
    logger.info(f"Attempting to schedule event: '{event_name}' from {start_time} to {end_time}")
    if attendees: logger.info(f"Attendees: {', '.join(attendees)}")
    if location: logger.info(f"Location: {location}")
    await asyncio.sleep(1.5)
    return f"Event '{event_name}' scheduled successfully. (Simulated)"

ScheduleEventTool = BaseTool(
    name="schedule_event",
    description="Schedules a new event on the user's calendar with specified name, start time, end time, attendees, and location.",
    func=schedule_event_func,
    schema=ScheduleEventArgs.model_json_schema()
)

class SetReminderArgs(BaseModel):
    reminder_text: str = Field(..., description="The text for the reminder.")
    time: str = Field(..., description="When the reminder should trigger (e.g., 'tomorrow 9 AM', 'in 30 minutes', '2025-07-01 14:00').")

async def set_reminder_func(reminder_text: str, time: str) -> str:
    """Simulates setting a reminder."""
    logger.info(f"Attempting to set reminder: '{reminder_text}' for {time}")
    await asyncio.sleep(1)
    return f"Reminder '{reminder_text}' set for {time}. (Simulated)"

SetReminderTool = BaseTool(
    name="set_reminder",
    description="Sets a reminder with a specific text and trigger time.",
    func=set_reminder_func,
    schema=SetReminderArgs.model_json_schema()
)

class PlannerAgent(BaseAgent):
    def __init__(self, llm_client: LLMClient, memory=None):
        super().__init__(
            name="PlannerAgent",
            role="Efficient Schedule and Task Planner",
            goal="Create, manage, and optimize schedules, set reminders, and track tasks effectively.",
            instructions=(
                "You are a meticulous planner. Use your `schedule_event` and `set_reminder` "
                "tools to manage the user's time and tasks. "
                "Always clarify dates, times, and specific details before committing to a plan. "
                "Consider existing commitments from memory when planning, but you do not have direct access to a calendar. "
                "Focus on creating actionable plans using your tools."
            ),
            llm_client=llm_client,
            memory=memory,
            tools=[ScheduleEventTool, SetReminderTool] # Assign planning tools
        )

    async def handle(self, user_input: str, multimodal_content: List[Union[str, PILImage]] = None) -> str:
        logger.info(f"[PlannerAgent] Planning schedule task for: {user_input}")
        
        async with cl.Step(name="LLM Planning & Tool Use", type="llm", parent_id=cl.get_current_step().id) as step:
            # The prompt will guide Gemini 1.5 Pro to use the appropriate planning tool
            response = await self.generate_response(user_input, multimodal_content=multimodal_content)
            step.output = f"Planning result: {response[:200]}..."
        
        return response