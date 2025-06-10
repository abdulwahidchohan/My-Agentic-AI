# config.py
# agentic_ai_framework/config.py
import os
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env file

# --- API Keys ---
# For Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# For OpenAI (if you still intend to use some OpenAI models or tools)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# For web search (e.g., Serper, SerpAPI)
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
# For Twilio (if you use it for voice/SMS)
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")


# --- API Endpoints ---
# Using the official Google Generative AI API:
GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta/" # For direct google-generativeai client
OPENAI_API_BASE = "https://api.openai.com/v1"

# --- Model Settings ---
MODEL_SETTINGS = {
    "default_model": "gemini-1.5-pro", # Default to Gemini for core tasks
    "gemini_model": "gemini-1.5-pro",
    "openai_model": "gpt-4o-mini", # Example if you want a cheaper, faster OpenAI model for specific tasks
    "temperature": 0.7, # Default temperature for LLM calls
    "max_tokens": 4096, # Max tokens for LLM responses
}

# --- Memory Settings ---
MEMORY_DB_PATH = "memory/chroma_db" # Path for ChromaDB persistence

# --- Logger Settings ---
LOG_FILE = "agentic_ai.log"