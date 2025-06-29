"""Gemini API client for generating finance-related responses."""

import google.generativeai as genai
import streamlit as st
from typing import List, Optional
from config.settings import settings


class GeminiClient:
    """Client for interacting with Google's Gemini API."""
    
    def __init__(self):
        """Initialize the Gemini client."""
        if not settings.validate_api_key():
            raise ValueError("GEMINI_API_KEY is not set or invalid")
        
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
    
    def generate_response(self, question: str, context_documents: List[str]) -> Optional[str]:
        """Generate a response based on the question and relevant context documents."""
        try:
            # Create the prompt with context
            prompt = self._create_prompt(question, context_documents)
            
            # Generate response
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=settings.MAX_TOKENS,
                    temperature=settings.TEMPERATURE,
                )
            )
            
            return response.text
            
        except Exception as e:
            st.error(f"Error generating response: {str(e)}")
            return None
    
    def _create_prompt(self, question: str, context_documents: List[str]) -> str:
        """Create a structured prompt for the Gemini model."""
        context = "\n\n".join([f"Document {i+1}:\n{doc}" for i, doc in enumerate(context_documents)])
        
        prompt = f"""You are a knowledgeable personal finance assistant. Your role is to provide helpful, accurate, and practical financial advice based ONLY on the provided context documents.

IMPORTANT GUIDELINES:
1. Base your response ONLY on the information provided in the context documents below
2. If the context doesn't contain enough information to fully answer the question, clearly state this limitation
3. Provide practical, actionable advice when possible
4. Use clear, easy-to-understand language
5. If asked about specific numbers or calculations, be precise and show your work
6. Always prioritize the user's financial safety and well-being
7. Do not provide advice that could be construed as professional financial planning without proper disclaimers

CONTEXT DOCUMENTS:
{context}

USER QUESTION: {question}

RESPONSE:
Please provide a comprehensive answer based on the context documents above. If the context is insufficient, suggest what additional information might be needed."""

        return prompt
    
    def test_connection(self) -> bool:
        """Test the connection to Gemini API."""
        try:
            response = self.model.generate_content("Hello")
            return bool(response.text)
        except Exception as e:
            st.error(f"Failed to connect to Gemini API: {str(e)}")
            return False


# Global client instance
@st.cache_resource
def get_gemini_client() -> Optional[GeminiClient]:
    """Get a cached Gemini client instance."""
    try:
        return GeminiClient()
    except Exception as e:
        st.error(f"Failed to initialize Gemini client: {str(e)}")
        return None 