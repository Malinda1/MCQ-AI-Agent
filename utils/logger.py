import logging
import os
from datetime import datetime

def setup_logger():
    log_level = os.getenv('LOG_LEVEL', 'INFO')
    
    # Make sure logs directory exists
    os.makedirs("logs", exist_ok=True)
    
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f'logs/mcq_agent_{datetime.now().strftime("%Y%m%d")}.log'),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger('MCQ_Agent')

logger = setup_logger()