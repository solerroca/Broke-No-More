"""Configuration settings for the Personal Finance Assistant app."""

import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    """Application settings and configuration."""
    
    # API Configuration - Support both Streamlit Cloud secrets and local env vars
    @property 
    def GEMINI_API_KEY(self) -> str:
        try:
            import streamlit as st
            return st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY", ""))
        except:
            return os.getenv("GEMINI_API_KEY", "")
    
    @property
    def GEMINI_MODEL(self) -> str:
        try:
            import streamlit as st
            return st.secrets.get("GEMINI_MODEL", os.getenv("GEMINI_MODEL", "gemini-1.5-flash"))
        except:
            return os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    
    # App Configuration
    APP_TITLE: str = os.getenv("APP_TITLE", "Personal Finance Assistant")
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "1000"))
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.7"))
    
    # Knowledge Base Configuration
    KNOWLEDGE_BASE_DIR: str = "data/knowledge_base"
    KNOWLEDGE_BASE_PATH: str = os.path.join(KNOWLEDGE_BASE_DIR, "knowledge_base.json")
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
    
    def validate_api_key(self) -> bool:
        """Validate that the Gemini API key is set."""
        api_key = self.GEMINI_API_KEY
        return bool(api_key and api_key != "your_gemini_api_key_here")
    
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

def get_settings() -> Settings:
    """Get the application settings instance."""
    return settings 