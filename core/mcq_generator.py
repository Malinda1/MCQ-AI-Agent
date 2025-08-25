import json
import re
from huggingface_hub import InferenceClient
from config.settings import settings
from models.mcq_models import MCQ, DifficultyLevel
from utils.logger import logger
from typing import List

class MCQGenerator:
    def __init__(self):
        self.client = InferenceClient(api_key=settings.HF_API_TOKEN)
    
    def generate_mcqs_from_domain(self, domain: str, count: int, difficulty: DifficultyLevel) -> List[MCQ]:
        prompt = self._create_domain_prompt(domain, count, difficulty)
        
        try:
            completion = self.client.chat.completions.create(
                model=settings.MAIN_MODEL,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response = completion.choices[0].message.content
            return self._parse_mcq_response(response)
            
        except Exception as e:
            logger.error(f"Error generating MCQs: {e}")
            return []
    
    def generate_mcqs_from_context(self, context: str, count: int, difficulty: DifficultyLevel, custom_prompt: str = None) -> List[MCQ]:
        prompt = self._create_context_prompt(context, count, difficulty, custom_prompt)
        
        try:
            completion = self.client.chat.completions.create(
                model=settings.MAIN_MODEL,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response = completion.choices[0].message.content
            return self._parse_mcq_response(response)
            
        except Exception as e:
            logger.error(f"Error generating MCQs from context: {e}")
            return []
    
    def _create_domain_prompt(self, domain: str, count: int, difficulty: DifficultyLevel) -> str:
        return f"""
        Generate {count} multiple choice questions about {domain} with {difficulty} difficulty level.
        
        IMPORTANT: Use only standard ASCII characters. Replace special characters as follows:
        - Use regular dash (-) instead of em-dash
        - Use regular apostrophe (') instead of curly quotes
        - Use standard bullet points or numbers
        - Avoid mathematical symbols that might not render properly
        
        Format each question as JSON:
        {{
            "question": "Question text using standard characters only",
            "options": [
                {{"text": "Option A", "is_correct": false}},
                {{"text": "Option B", "is_correct": true}},
                {{"text": "Option C", "is_correct": false}},
                {{"text": "Option D", "is_correct": false}}
            ],
            "explanation": "Brief explanation of correct answer using standard characters",
            "difficulty": "{difficulty}"
        }}
        
        Return as JSON array of questions. Ensure all text uses standard ASCII characters only.
        """
    
    def _create_context_prompt(self, context: str, count: int, difficulty: DifficultyLevel, custom_prompt: str) -> str:
        # Clean the context first
        cleaned_context = self._clean_text(context)
        
        base_prompt = f"""
        Based on the following context, generate {count} multiple choice questions with {difficulty} difficulty:
        
        Context: {cleaned_context[:2000]}...
        
        {custom_prompt if custom_prompt else ''}
        
        IMPORTANT: Use only standard ASCII characters in your response. Replace special characters as follows:
        - Use regular dash (-) instead of em-dash
        - Use regular apostrophe (') instead of curly quotes
        - Use standard bullet points or numbers
        - Avoid mathematical symbols that might not render properly
        """
        return base_prompt + self._get_format_instructions(difficulty)
    
    def _get_format_instructions(self, difficulty: DifficultyLevel) -> str:
        return f"""
        Format as JSON array with this structure:
        [{{
            "question": "Question text using standard characters only",
            "options": [
                {{"text": "Option A", "is_correct": false}},
                {{"text": "Option B", "is_correct": true}},
                {{"text": "Option C", "is_correct": false}},
                {{"text": "Option D", "is_correct": false}}
            ],
            "explanation": "Brief explanation using standard characters",
            "difficulty": "{difficulty}"
        }}]
        
        Ensure all text uses standard ASCII characters only.
        """
    
    def _clean_text(self, text: str) -> str:
        """Clean text by replacing problematic characters with standard ones"""
        if not text:
            return ""
        
        # Dictionary of character replacements
        replacements = {
            # Em-dash and en-dash
            '—': '-',
            '–': '-',
            '―': '-',
            
            # Quotes
            '"': '"',
            '"': '"',
            ''': "'",
            ''': "'",
            
            # Bullets and special symbols
            '•': '*',
            '◦': '-',
            '▪': '*',
            '▫': '-',
            '■': '*',
            '□': '-',
            
            # Mathematical symbols
            '×': 'x',
            '÷': '/',
            '±': '+/-',
            '∑': 'Sum',
            '∏': 'Product',
            '∞': 'infinity',
            '≈': '~=',
            '≤': '<=',
            '≥': '>=',
            '≠': '!=',
            
            # Other problematic characters
            '…': '...',
            '™': '(TM)',
            '©': '(C)',
            '®': '(R)',
        }
        
        # Apply replacements
        cleaned_text = text
        for old_char, new_char in replacements.items():
            cleaned_text = cleaned_text.replace(old_char, new_char)
        
        # Remove any remaining non-ASCII characters
        cleaned_text = ''.join(char if ord(char) < 128 else '?' for char in cleaned_text)
        
        return cleaned_text
    
    def _parse_mcq_response(self, response: str) -> List[MCQ]:
        try:
            # Clean the response first
            cleaned_response = self._clean_text(response)
            
            # Extract JSON from response
            start_idx = cleaned_response.find('[')
            end_idx = cleaned_response.rfind(']') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = cleaned_response[start_idx:end_idx]
                mcq_data = json.loads(json_str)
                
                # Clean each MCQ data before creating objects
                cleaned_mcqs = []
                for mcq in mcq_data:
                    cleaned_mcq = {
                        "question": self._clean_text(mcq.get("question", "")),
                        "options": [
                            {
                                "text": self._clean_text(option.get("text", "")),
                                "is_correct": option.get("is_correct", False)
                            }
                            for option in mcq.get("options", [])
                        ],
                        "explanation": self._clean_text(mcq.get("explanation", "")),
                        "difficulty": mcq.get("difficulty", "medium")
                    }
                    cleaned_mcqs.append(MCQ(**cleaned_mcq))
                
                return cleaned_mcqs
            
        except Exception as e:
            logger.error(f"Error parsing MCQ response: {e}")
        
        return []