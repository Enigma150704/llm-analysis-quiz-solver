"""
Configuration management for the LLM Analysis Quiz Solver
"""
import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables
load_dotenv()


class Config:
    """Application configuration"""
    
    # API Keys
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # Quiz Solver Configuration
    SECRET: str = os.getenv("SECRET", "")
    EMAIL: str = os.getenv("EMAIL", "")
    
    # Prompt Configuration
    SYSTEM_PROMPT: str = os.getenv("SYSTEM_PROMPT", "")
    USER_PROMPT: str = os.getenv("USER_PROMPT", "")
    
    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Quiz Solving Configuration
    MAX_QUIZ_TIME_SECONDS: int = 180  # 3 minutes
    TIMEOUT_SECONDS: int = 30
    MAX_RETRIES: int = 3
    
    @classmethod
    def validate(cls) -> tuple[bool, Optional[str]]:
        """Validate that required configuration is present"""
        if not cls.OPENAI_API_KEY:
            return False, "OPENAI_API_KEY is required"
        if not cls.SECRET:
            return False, "SECRET is required"
        if not cls.EMAIL:
            return False, "EMAIL is required"
        if len(cls.SYSTEM_PROMPT) > 100:
            return False, "SYSTEM_PROMPT must be 100 characters or less"
        if len(cls.USER_PROMPT) > 100:
            return False, "USER_PROMPT must be 100 characters or less"
        return True, None

