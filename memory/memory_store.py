# memory_store.py
# agentic_ai_framework/memory/memory_store.py
from chromadb import Client, Settings
from chromadb.utils import embedding_functions
from config import MEMORY_DB_PATH, GEMINI_API_KEY
from utils.logger import setup_logger
from typing import List, Dict, Any
import os
import asyncio

logger = setup_logger(__name__)

class MemoryStore:
    def __init__(self):
        if not GEMINI_API_KEY:
            logger.error("GEMINI_API_KEY is required for GeminiEmbeddingFunction. MemoryStore not initialized.")
            self.client = None
            self.collection = None
            return

        self.embedding_function = embedding_functions.GoogleGenerativeAiEmbeddingFunction(api_key=GEMINI_API_KEY)
        
        # Ensure the memory directory exists
        os.makedirs(MEMORY_DB_PATH, exist_ok=True)
        
        self.client = Client(Settings(
            persist_directory=MEMORY_DB_PATH
        ))
        self.collection_name = "agentic_ai_memory"
        
        try:
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                embedding_function=self.embedding_function
            )
            logger.info(f"MemoryStore initialized successfully with collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB collection: {e}")
            self.collection = None

    async def add_to_memory(self, text: str, metadata: Dict[str, Any] = None) -> bool:
        """Adds text content to the memory store."""
        if not self.collection:
            logger.error("MemoryStore collection not initialized.")
            return False
        try:
            await asyncio.sleep(0.1) # Simulate async operation
            # ChromaDB expects IDs for documents
            doc_id = f"doc_{self.collection.count() + 1}"
            self.collection.add(
                documents=[text],
                metadatas=[metadata if metadata else {}],
                ids=[doc_id]
            )
            logger.info(f"Added document to memory: {doc_id}")
            return True
        except Exception as e:
            logger.error(f"Error adding to memory: {e}")
            return False

    async def query_memory(self, query: str, n_results: int = 3) -> List[str]:
        """Queries the memory store for relevant documents."""
        if not self.collection:
            logger.error("MemoryStore collection not initialized.")
            return []
        try:
            await asyncio.sleep(0.1) # Simulate async operation
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            documents = results.get('documents', [[]])[0]
            logger.info(f"Queried memory for '{query}', found {len(documents)} results.")
            return documents
        except Exception as e:
            logger.error(f"Error querying memory: {e}")
            return []