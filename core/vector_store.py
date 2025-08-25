from pinecone import Pinecone
from huggingface_hub import InferenceClient
from typing import List
from config.settings import settings
from utils.logger import logger
import hashlib
import uuid

class VectorStore:
    def __init__(self):
        # Initialize Pinecone client with the new API
        self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        self.index = self.pc.Index(settings.PINECONE_INDEX_NAME)
        self.embedding_client = InferenceClient(
            api_key=settings.HF_API_TOKEN
        )
    
    def add_document(self, text: str, metadata: dict = None):
        """Add document to vector store"""
        try:
            # Create embeddings
            embedding = self.embedding_client.feature_extraction(
                text,
                model=settings.EMBEDDING_MODEL
            )
            
            # Generate unique ID
            doc_id = str(uuid.uuid4())
            
            # Upsert to Pinecone
            self.index.upsert([
                {
                    "id": doc_id,
                    "values": embedding,
                    "metadata": metadata or {"text": text[:500]}
                }
            ])
            
            logger.info(f"Document added to vector store with ID: {doc_id}")
            return doc_id
            
        except Exception as e:
            logger.error(f"Error adding document to vector store: {e}")
            return None
    
    def search_similar(self, query: str, top_k: int = 3) -> List[str]:
        """Search for similar documents"""
        try:
            query_embedding = self.embedding_client.feature_extraction(
                query,
                model=settings.EMBEDDING_MODEL
            )
            
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True
            )
            
            return [match.metadata.get("text", "") for match in results.matches]
            
        except Exception as e:
            logger.error(f"Error searching vector store: {e}")
            return []