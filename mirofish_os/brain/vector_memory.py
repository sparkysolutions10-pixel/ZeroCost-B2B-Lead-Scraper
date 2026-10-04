import logging
import chromadb
from chromadb.config import Settings
import os

logger = logging.getLogger("mirofish.brain.vector_memory")

class VectorMemory:
    """
    True AGI Long-Term Memory (Vector Database).
    Uses ChromaDB to store and semantically search past experiences, emails, and data.
    This gives Sparky 5.1 the ability to 'learn' from past mistakes and context.
    """
    def __init__(self, db_path: str = "./mirofish_vector_db"):
        self.db_path = db_path
        os.makedirs(self.db_path, exist_ok=True)
        
        # Initialize ChromaDB Local Persistent Client
        try:
            self.client = chromadb.PersistentClient(path=self.db_path)
            # Use the default embedding model (all-MiniLM-L6-v2) automatically downloaded by Chroma
            self.collection = self.client.get_or_create_collection(name="sparky_agi_memory")
            self.is_ready = True
            logger.info(f"dYs? Vector Memory (ChromaDB) initialized successfully at {self.db_path}")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            self.is_ready = False

    def store_memory(self, memory_id: str, content: str, metadata: dict = None):
        """Stores a semantic memory."""
        if not self.is_ready: return
        
        try:
            self.collection.add(
                documents=[content],
                metadatas=[metadata or {}],
                ids=[memory_id]
            )
            logger.info(f"dY" Memory stored: {memory_id}")
        except Exception as e:
            logger.error(f"Error storing memory: {e}")

    def recall_memory(self, query: str, n_results: int = 3):
        """Semantically searches for related past memories based on the query."""
        if not self.is_ready: return []
        
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            return results.get('documents', [[]])[0]
        except Exception as e:
            logger.error(f"Error recalling memory: {e}")
            return []

vector_memory = VectorMemory()
