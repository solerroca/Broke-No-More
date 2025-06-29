"""Configuration settings for the Personal Finance Assistant app."""

import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    """Application settings and configuration."""
    
    # API Configuration
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-pro")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    
    # App Configuration
    APP_TITLE: str = os.getenv("APP_TITLE", "Personal Finance Assistant")
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "1000"))
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.7"))
    
    # Knowledge Base Configuration
    KNOWLEDGE_BASE_DIR: str = "data/knowledge_base"
    CHROMA_DB_DIR: str = "data/chroma_db"
    SUPPORTED_FILE_TYPES: list = [".txt", ".pdf", ".docx"]
    MAX_FILE_SIZE_MB: int = 10
    
    # RAG Configuration
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    TOP_K_RESULTS: int = 5
    SIMILARITY_THRESHOLD: float = 0.7
    
    # UI Configuration
    PAGE_TITLE: str = "💰 Personal Finance Assistant"
    PAGE_ICON: str = "💰"
    LAYOUT: str = "wide"
    
    @classmethod
    def validate_api_key(cls) -> bool:
        """Validate that the Gemini API key is set."""
        return bool(cls.GEMINI_API_KEY and cls.GEMINI_API_KEY != "your_gemini_api_key_here")
    
    @classmethod
    def get_file_upload_config(cls) -> Dict[str, Any]:
        """Get file upload configuration for Streamlit."""
        return {
            "type": cls.SUPPORTED_FILE_TYPES,
            "accept_multiple_files": True,
            "help": f"Upload documents (max {cls.MAX_FILE_SIZE_MB}MB each). Supported formats: {', '.join(cls.SUPPORTED_FILE_TYPES)}"
        }

# Global settings instance
settings = Settings() 