from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class MCQSource(str, Enum):
    MAIN_BRAIN = "main_brain"
    SERP_API = "serp_api"
    WIKIPEDIA = "wikipedia"

class MCQOption(BaseModel):
    text: str
    is_correct: bool

class MCQ(BaseModel):
    question: str
    options: List[MCQOption]
    explanation: str
    difficulty: DifficultyLevel

class MCQRequest(BaseModel):
    domain: str
    count: int
    difficulty: DifficultyLevel
    source: MCQSource
    email: Optional[str] = None
    custom_prompt: Optional[str] = None

class DocumentMCQRequest(BaseModel):
    count: int
    difficulty: DifficultyLevel
    email: Optional[str] = None
    custom_prompt: Optional[str] = None