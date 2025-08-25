import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # HuggingFace
    HF_API_TOKEN = os.getenv("HF_API_TOKEN")
    MAIN_MODEL = "openai/gpt-oss-120b"
    EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"
    
    # Pinecone
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "mcq-documents")
    
    # SendGrid
    SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
    
    # Google Drive
    GOOGLE_DRIVE_FOLDER_ID = os.getenv("GOOGLE_DRIVE_FOLDER_ID")
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
    GOOGLE_REFRESH_TOKEN = os.getenv("GOOGLE_REFRESH_TOKEN")
    
    # SERP API
    SERP_API_KEY = os.getenv("SERP_API_KEY")

settings = Settings()