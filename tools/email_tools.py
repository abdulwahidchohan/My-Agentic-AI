# email_tools.py
# agentic_ai_framework/tools/email_tools.py
import asyncio
from tools import BaseTool
from utils.logger import setup_logger
from pydantic import BaseModel, Field

logger = setup_logger(__name__)

class SendEmailArgs(BaseModel):
    to_address: str = Field(..., description="The recipient's email address.")
    subject: str = Field(..., description="The subject line of the email.")
    body: str = Field(..., description="The body content of the email.")
    cc_address: str = Field(None, description="Optional CC recipient's email address.")
    bcc_address: str = Field(None, description="Optional BCC recipient's email address.")

async def send_email_func(to_address: str, subject: str, body: str, cc_address: str = None, bcc_address: str = None) -> str:
    """
    Simulates sending an email. In a real application, this would integrate with an email API (e.g., Gmail API, Microsoft Graph).
    """
    logger.info(f"Attempting to send email to: {to_address}")
    logger.info(f"Subject: {subject}")
    logger.info(f"Body: {body[:100]}...") # Log first 100 chars
    if cc_address: logger.info(f"CC: {cc_address}")
    if bcc_address: logger.info(f"BCC: {bcc_address}")

    await asyncio.sleep(2) # Simulate network delay for sending email

    return f"Email to {to_address} with subject '{subject}' simulated as sent. (Actual sending disabled for safety)"

SendEmailTool = BaseTool(
    name="send_email",
    description="Sends an email to a specified recipient with a subject and body. Can include CC and BCC.",
    func=send_email_func,
    schema=SendEmailArgs.model_json_schema()
)

class ReadEmailArgs(BaseModel):
    query: str = Field(..., description="A query to search for emails (e.g., 'latest unread emails', 'emails from John Doe about project X').")
    max_results: int = Field(3, description="Maximum number of emails to retrieve.")

async def read_email_func(query: str, max_results: int = 3) -> str:
    """
    Simulates reading emails based on a query. In a real application, this would integrate with an email API.
    """
    logger.info(f"Attempting to read emails with query: '{query}' (Max results: {max_results})")
    await asyncio.sleep(2) # Simulate delay

    mock_emails = [
        {"from": "alice@example.com", "subject": "Project X Update", "body": "Hi team, the project is on track. Meeting next week."},
        {"from": "bob@example.com", "subject": "Invoice 123 Ready", "body": "Your invoice is attached. Please review."},
        {"from": "charlie@example.com", "subject": "Lunch Today?", "body": "Are you free for lunch today at 1 PM?"}
    ]

    found_emails = [e for e in mock_emails if query.lower() in (e['subject'] + e['body'] + e['from']).lower()]

    if found_emails:
        formatted_emails = []
        for i, email in enumerate(found_emails[:max_results]):
            formatted_emails.append(f"Email {i+1} - From: {email['from']}, Subject: {email['subject']}, Body: {email['body'][:50]}...")
        return "Found emails:\n" + "\n".join(formatted_emails)
    return "No emails found matching your query."

ReadEmailTool = BaseTool(
    name="read_email",
    description="Reads emails based on a specified query and returns a summary of the top results.",
    func=read_email_func,
    schema=ReadEmailArgs.model_json_schema()
)