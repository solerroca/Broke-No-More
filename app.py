"""Personal Finance Assistant - No Upload Version"""

import streamlit as st
import pandas as pd
from datetime import datetime
import os
from pathlib import Path
from typing import Optional
import base64

from src.gemini_client import GeminiClient
from src.knowledge_base_simple import SimpleKnowledgeBase
from src.utils import validate_finance_question, process_document
from config.settings import get_settings

# Page configuration
st.set_page_config(
    page_title="💰 Personal Finance Q&A Assistant",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .info-box {
        background-color: #f0f9ff;
        border-left: 4px solid #3b82f6;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    
    .warning-box {
        background-color: #fef3c7;
        border-left: 4px solid #f59e0b;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    
    .success-box {
        background-color: #f0fdf4;
        border-left: 4px solid #10b981;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    
    .stButton > button {
        width: 100%;
        background-color: #3b82f6;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: background-color 0.3s;
    }
    
    .stButton > button:hover {
        background-color: #1d4ed8;
    }
    
    /* Hide sidebar */
    .css-1d391kg {
        display: none;
    }
    
    /* Center main content */
    .main .block-container {
        padding-top: 2rem;
        max-width: 800px;
        margin: 0 auto;
    }
</style>
""", unsafe_allow_html=True)

def initialize_app():
    """Initialize the application with settings and clients."""
    try:
        settings = get_settings()
        
        # Initialize Gemini client
        if 'gemini_client' not in st.session_state:
            st.session_state.gemini_client = GeminiClient(settings.GEMINI_API_KEY)
        
        # Initialize knowledge base
        if 'knowledge_base' not in st.session_state:
            st.session_state.knowledge_base = SimpleKnowledgeBase(settings.KNOWLEDGE_BASE_PATH)
            
        # Auto-load documents from the documents folder
        if 'documents_loaded' not in st.session_state:
            load_predefined_documents()
            st.session_state.documents_loaded = True
            
        return True
        
    except Exception as e:
        st.error(f"❌ **Error initializing application:** {str(e)}")
        st.markdown("""
        <div class="warning-box">
            <strong>Troubleshooting:</strong>
            <ul>
                <li>Make sure your .env file contains a valid GEMINI_API_KEY</li>
                <li>Check that all required files are present</li>
                <li>Restart the application if issues persist</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        return False

def load_predefined_documents():
    """Load documents from the predefined documents folder."""
    documents_folder = Path("data/documents")
    
    if not documents_folder.exists():
        documents_folder.mkdir(parents=True, exist_ok=True)
        return
    
    # Get all supported document files
    supported_extensions = ['.txt', '.pdf', '.docx']
    document_files = []
    
    for ext in supported_extensions:
        document_files.extend(list(documents_folder.glob(f"*{ext}")))
    
    if not document_files:
        return
    
    # Load documents into knowledge base (silently)
    loaded_count = 0
    for doc_path in document_files:
        try:
            # Check if document is already in knowledge base
            existing_docs = st.session_state.knowledge_base.list_documents()
            doc_titles = [doc.get('title', doc.get('filename', '')) for doc in existing_docs]
            
            if doc_path.name not in doc_titles:
                # Read and process the document
                content = process_document(str(doc_path))
                
                if content:
                    st.session_state.knowledge_base.add_document(
                        title=doc_path.name,
                        content=content,
                        metadata={
                            'file_type': doc_path.suffix.lower(),
                            'file_size': doc_path.stat().st_size,
                            'added_date': datetime.now().isoformat(),
                            'source': 'predefined'
                        }
                    )
                    loaded_count += 1
                    
        except Exception as e:
            # Silent loading - don't show warnings
            pass

def load_book_image():
    """Load and encode the promotional book image."""
    try:
        image_path = Path("static/images/broke-no-more-transparent.png")
        print(f"🔍 Looking for image at: {image_path.absolute()}")
        print(f"📁 Image exists: {image_path.exists()}")
        
        if image_path.exists():
            with open(image_path, "rb") as img_file:
                image_data = base64.b64encode(img_file.read()).decode()
                print(f"✅ Image loaded successfully! Size: {len(image_data)} characters")
                return image_data
        else:
            print("❌ Image file not found - showing text-only promotional section")
            return None
    except Exception as e:
        print(f"⚠️ Error loading image: {e}")
        return None

def main():
    """Main application function."""
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>💰 Personal Finance Q&A Assistant</h1>
        <p>Get expert financial advice powered by AI and curated knowledge</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Promotional section for "Broke No More" book
    book_image_data = load_book_image()
    
    if book_image_data:
        # Show promotional section with actual book image
        st.markdown(f"""
        <div style="text-align: center; margin: 30px 0; padding: 20px; background: white; border-radius: 15px; box-shadow: 0 4px 20px rgba(0,0,0,0.1);">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px 20px; border-radius: 10px; margin-bottom: 20px; display: inline-block;">
                <h3 style="color: white; margin-bottom: 3px; font-size: 1.1em;">📚 App Powered by the Book</h3>
                <h2 style="color: #fff; margin: 0; font-weight: 700; font-size: 1.8em;">'Broke No More'</h2>
            </div>
            <a href="https://www.amazon.com/Broke-More-Easy-Follow-Strategies/dp/196628800X/ref=sr_1_2?crid=1I2229DFKOWE2&dib=eyJ2IjoiMSJ9.Y3EC7BYPotcNcCpQkFuWgyTURtZXDgSMa7v87YOnt6xEb5zqzgwRhigftpmGRMm4li93dXytUd--woy-3Rgy2IyLVY6WKfoqkPhv2wCyF6Hfw0BtnlDDAko1UEaUoucVe6Xkm91djx57Bhqy8Dzs2eNZKDL91bhxdBCwFUA-rQUqzyTIp7oB0OG_dWcP4nj1xEcm0eVBjM4sSSdmHdwiq2BQAFp1p9_rLQWo2z-n0_M.ogRhG6GClaDbNPhSUSXTVFswk4_0KRCJLAb9iR8n0S4&dib_tag=se&keywords=broke+no+more&qid=1751304047&sprefix=broke+no+more%2Caps%2C171&sr=8-2" target="_blank" style="text-decoration: none;">
                <img src="data:image/png;base64,{book_image_data}" alt="Broke No More - The Gen Z Guide to Money Mastery" style="max-width: 300px; height: auto; border-radius: 8px; transition: transform 0.3s ease; cursor: pointer;" onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
            </a>
            <p style="margin-top: 15px; color: #555; font-size: 0.9em;">📚 Link to the book</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Show text-only promotional section if image not available
        st.markdown("""
        <div style="text-align: center; margin: 30px 0; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px;">
            <div style="background: white; padding: 20px; border-radius: 10px; display: inline-block; box-shadow: 0 8px 25px rgba(0,0,0,0.15);">
                <h3 style="color: #333; margin-bottom: 5px;">📚 App Powered by the Book</h3>
                <h4 style="color: #2563eb; margin: 0 0 10px 0; font-weight: 600;">'Broke No More'</h4>
                <p style="color: #666; margin-bottom: 15px;">The Gen Z Guide to Money Mastery in 5 Weeks</p>
                <a href="https://www.amazon.com/Broke-More-Easy-Follow-Strategies/dp/196628800X/ref=sr_1_2?crid=1I2229DFKOWE2&dib=eyJ2IjoiMSJ9.Y3EC7BYPotcNcCpQkFuWgyTURtZXDgSMa7v87YOnt6xEb5zqzgwRhigftpmGRMm4li93dXytUd--woy-3Rgy2IyLVY6WKfoqkPhv2wCyF6Hfw0BtnlDDAko1UEaUoucVe6Xkm91djx57Bhqy8Dzs2eNZKDL91bhxdBCwFUA-rQUqzyTIp7oB0OG_dWcP4nj1xEcm0eVBjM4sSSdmHdwiq2BQAFp1p9_rLQWo2z-n0_M.ogRhG6GClaDbNPhSUSXTVFswk4_0KRCJLAb9iR8n0S4&dib_tag=se&keywords=broke+no+more&qid=1751304047&sprefix=broke+no+more%2Caps%2C171&sr=8-2" target="_blank" style="background: #2563eb; color: white; padding: 12px 24px; border-radius: 6px; text-decoration: none; display: inline-block; font-weight: 600; transition: background 0.3s ease;" onmouseover="this.style.background='#1d4ed8'" onmouseout="this.style.background='#2563eb'">
                    📖 Purchase on Amazon
                </a>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Initialize application
    if not initialize_app():
        st.stop()
    
    # Main content area - full width
    st.markdown("## 💬 Ask Your Personal Finance Question")
    
    # Initialize selected question in session state
    if 'selected_question' not in st.session_state:
        st.session_state.selected_question = ""
    
    # Question input
    user_question = st.text_area(
        "What would you like to know about personal finance?",
        value=st.session_state.selected_question,
        placeholder="e.g., How should I start investing as a beginner? What's the best way to create a budget?",
        height=120,
        help="Ask specific questions about budgeting, investing, saving, debt management, or other financial topics."
    )
    
    # Submit button
    if st.button("🔍 Get Expert Answer", type="primary"):
        if not user_question.strip():
            st.warning("📝 Please enter a question first.")
        else:
            # Clear the selected question from session state
            st.session_state.selected_question = ""
            
            # Validate if it's a finance-related question
            if not validate_finance_question(user_question):
                st.markdown("""
                <div class="warning-box">
                    <strong>⚠️ Not a finance question</strong><br>
                    This app is designed for personal finance questions. Please ask about topics like:
                    budgeting, saving, investing, debt management, retirement planning, insurance, or taxes.
                </div>
                """, unsafe_allow_html=True)
            else:
                # Process the question
                with st.spinner("🤔 Thinking and analyzing your question..."):
                    try:
                        # Search knowledge base
                        relevant_docs = st.session_state.knowledge_base.search(user_question, top_k=3)
                        
                        # Generate response using Gemini
                        response = st.session_state.gemini_client.generate_response(
                            question=user_question,
                            context_documents=relevant_docs
                        )
                        
                        # Display response - clean format without confidence or sources
                        st.markdown("### 💡 Expert Answer")
                        st.markdown(response['answer'])
                        
                    except Exception as e:
                        st.error(f"❌ **Error generating response:** {str(e)}")
                        st.markdown("""
                        <div class="warning-box">
                            <strong>Troubleshooting:</strong>
                            <ul>
                                <li>Check your internet connection</li>
                                <li>Verify your Gemini API key is valid</li>
                                <li>Try rephrasing your question</li>
                            </ul>
                        </div>
                        """, unsafe_allow_html=True)
    
    # Tips section
    st.markdown("---")
    st.markdown("## 📋 Quick Tips")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **💡 How to get better answers:**
        
        ✅ **Be specific**  
        "How much should I save for retirement at age 30?" vs "Tell me about retirement"
        
        ✅ **Include context**  
        "I'm 25, make $50k, want to start investing - where do I begin?"
        
        ✅ **Ask follow-ups**  
        Build on previous answers for deeper insights
        """)
    
    with col2:
        st.markdown("""
        **📚 Topics I can help with:**
        - 💰 Budgeting & saving strategies
        - 📈 Investment basics & strategies  
        - 💳 Debt management & payoff plans
        - 🏠 Home buying & mortgages
        - 🛡️ Insurance & protection planning
        - 📊 Tax planning & optimization
        - 💼 Retirement planning
        """)
    
    # Sample questions
    st.markdown("### 🎯 Example Questions")
    sample_questions = [
        "What's the 50/30/20 budgeting rule?",
        "How do I start an emergency fund?",
        "What's the difference between 401k and IRA?",
        "Should I pay off debt or invest first?",
        "How much house can I afford?",
    ]
    
    # Display sample questions in columns
    cols = st.columns(len(sample_questions))
    for i, question in enumerate(sample_questions):
        with cols[i]:
            if st.button(f"💭 {question}", key=f"sample_{i}"):
                st.session_state.selected_question = question
                st.rerun()
    
    # Disclaimer section - always visible for legal compliance
    st.markdown("---")
    
    st.markdown("""
    <div style="background-color: #f8f9fa; border: 1px solid #e9ecef; border-radius: 6px; padding: 16px; margin: 20px 0;">
        <h5 style="color: #495057; margin-top: 0; margin-bottom: 12px; font-weight: 500;">Disclaimer</h5>
        <div style="font-size: 0.85em; color: #6c757d; line-height: 1.4;">
        The information provided by this Personal Finance Q&A Assistant is for educational and informational purposes only and should not be considered as personalized financial, investment, tax, or legal advice. This AI-powered tool provides general guidance based on common financial principles and may not be suitable for your specific financial situation.
        <br><br>
        Always consult with qualified financial advisors, tax professionals, or other licensed experts before making important financial decisions. Past performance does not guarantee future results. All investments carry risk, including potential loss of principal.
        <br><br>
        By using this service, you acknowledge that you are solely responsible for your financial decisions and that neither the app nor its creators are liable for any financial losses or damages resulting from your use of this information.
        </div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 