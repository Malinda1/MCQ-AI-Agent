import uvicorn
from api.routes import app
from utils.logger import logger
import os

def create_directories():
    """Create necessary directories"""
    directories = ['logs', 'uploads', 'outputs']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

if __name__ == "__main__":
    create_directories()
    logger.info("Starting MCQ AI Agent...")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True
    )