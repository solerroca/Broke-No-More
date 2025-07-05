"""Gemini API client for generating finance-related responses."""

import google.generativeai as genai
import streamlit as st
from typing import List, Optional, Dict, Any
from config.settings import settings


class GeminiClient:
    """Client for interacting with Google's Gemini API."""
    
    def __init__(self, api_key: str = None):
        """Initialize the Gemini client."""
        # Use provided API key or fall back to settings
        self.api_key = api_key or settings.GEMINI_API_KEY
        
        if not self.api_key or self.api_key == "your_gemini_api_key_here":
            raise ValueError("GEMINI_API_KEY is not set or invalid")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
    
    def generate_response(self, question: str = None, context_documents: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate a response based on the question and relevant context documents."""
        try:
            # Handle different parameter formats
            if context_documents is None:
                context_documents = []
            
            # Extract text content from context documents
            if context_documents and isinstance(context_documents[0], dict):
                context_texts = [doc.get('content', str(doc)) for doc in context_documents]
            else:
                context_texts = [str(doc) for doc in context_documents]
            
            # Create the prompt with context
            prompt = self._create_prompt(question, context_texts)
            
            # Generate response
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=settings.MAX_TOKENS,
                    temperature=settings.TEMPERATURE,
                )
            )
            
            # Return structured response
            return {
                'answer': response.text,
                'confidence': 0.8 if context_texts else 0.5,  # Simple confidence scoring
                'sources': context_documents[:3] if context_documents else []  # Return top 3 sources
            }
            
        except Exception as e:
            st.error(f"Error generating response: {str(e)}")
            return {
                'answer': "I'm sorry, I encountered an error while generating a response. Please try again.",
                'confidence': 0.0,
                'sources': []
            }
    
    def _create_prompt(self, question: str, context_documents: List[str]) -> str:
        """Create a structured prompt for the Gemini model."""
        if context_documents:
            context = "\n\n".join([f"Reference Material {i+1}:\n{doc}" for i, doc in enumerate(context_documents)])
        else:
            context = "No specific reference material provided."
        
        prompt = f"""You are a highly knowledgeable Certified Financial Planner (CFP) and personal finance expert with over 20 years of experience helping people achieve their financial goals. You have deep expertise in budgeting, investing, debt management, retirement planning, insurance, and tax strategies.

IMPORTANT - Your Response Style:
• Respond as a confident financial expert and educator
• Use a warm, educational, and encouraging tone
• Provide practical, actionable advice
• Break down complex concepts into easy-to-understand explanations
• Use examples and analogies when helpful
• Never mention "based on provided text" or reference materials
• Speak directly to the person asking the question
• Be authoritative but approachable

GUIDELINES:
• Provide comprehensive, practical financial advice
• Use clear, jargon-free language while maintaining expertise
• Include specific steps or recommendations when appropriate
• Always prioritize the person's financial safety and well-being
• If you need more information to give the best advice, ask clarifying questions
• Include helpful tips and best practices
• Make your advice actionable and specific

CRITICAL - RESPONSE FORMAT AND STRUCTURE:
Write your response in a natural, conversational style that flows well. Start directly with helpful information about the topic - no greetings or introductory phrases needed.

Structure your content for maximum readability:
• Use clear subheaders (##) to organize main sections such as "Understanding the Basics", "Key Steps", "Important Considerations", "Common Mistakes", or "Next Steps"
• Write focused paragraphs of 3-4 sentences each, with each paragraph covering one main idea
• Use bullet points strategically for lists of steps, benefits, tips, or examples
• End with practical next steps or encouragement

Make sure your response flows naturally from section to section without artificial transitions or structural announcements.

IMPORTANT - DOCUMENT REFERENCES:
• Never mention "based on provided text", "reference materials", "documents", or similar phrases
• Do not cite specific PDFs or reference sources in your response
• Occasionally (every few responses), you may naturally reference "Broke No More" by Sasha Albright as a helpful financial resource
• Present all advice as your own expert knowledge and experience

REFERENCE MATERIALS (use this knowledge naturally in your response):
{context}

QUESTION: {question}

Provide a comprehensive, well-structured expert response that educates and empowers the person to make informed financial decisions:"""

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