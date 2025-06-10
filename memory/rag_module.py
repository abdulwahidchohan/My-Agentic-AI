# rag_module.py
# agentic_ai_framework/memory/rag_module.py
from memory.memory_store import MemoryStore
from utils.logger import setup_logger
from typing import List, Dict, Any

logger = setup_logger(__name__)

class RAGModule:
    def __init__(self, memory_store: MemoryStore):
        self.memory_store = memory_store
        logger.info("RAGModule initialized.")

    async def query_memory(self, query: str, n_results: int = 3) -> List[str]:
        """
        Retrieves relevant documents from memory based on a query.
        """
        if not self.memory_store.collection:
            logger.warning("Memory store not available for RAG query.")
            return []
        
        return await self.memory_store.query_memory(query, n_results)

    async def add_to_memory(self, text: str, metadata: Dict[str, Any] = None) -> bool:
        """
        Adds text to the memory store.
        """
        if not self.memory_store.collection:
            logger.warning("Memory store not available for adding content.")
            return False
            
        return await self.memory_store.add_to_memory(text, metadata)