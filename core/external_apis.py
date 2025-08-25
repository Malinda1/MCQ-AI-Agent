import requests
import wikipedia
from config.settings import settings
from utils.logger import logger

class ExternalAPIs:
    
    @staticmethod
    def search_serp_api(query: str, num_results: int = 5) -> str:
        """Search using SERP API"""
        try:
            url = "https://serpapi.com/search"
            params = {
                "api_key": settings.SERP_API_KEY,
                "q": query,
                "num": num_results,
                "engine": "google"
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            # Extract organic results
            results = []
            for result in data.get("organic_results", []):
                results.append(f"{result.get('title', '')}: {result.get('snippet', '')}")
            
            return "\n".join(results)
            
        except Exception as e:
            logger.error(f"SERP API error: {e}")
            return ""
    
    @staticmethod
    def search_wikipedia(query: str, sentences: int = 5) -> str:
        """Search Wikipedia"""
        try:
            summary = wikipedia.summary(query, sentences=sentences)
            return summary
            
        except wikipedia.exceptions.DisambiguationError as e:
            # Try first option
            try:
                return wikipedia.summary(e.options[0], sentences=sentences)
            except:
                return ""
        except Exception as e:
            logger.error(f"Wikipedia error: {e}")
            return ""