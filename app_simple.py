"""Personal Finance Assistant - No Upload Version"""

import streamlit as st
import pandas as pd
from datetime import datetime
import os
from pathlib import Path
from typing import Optional

from src.gemini_client import GeminiClient
from src.knowledge_base_simple import SimpleKnowledgeBase
from src.utils import validate_finance_question, process_document
from config.settings import get_settings

# Page configuration
st.set_page_config(
    page_title="💰 Personal Finance Q&A Assistant",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
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
        st.info("📁 Documents folder not found. Creating it now...")
        documents_folder.mkdir(parents=True, exist_ok=True)
        return
    
    # Get all supported document files
    supported_extensions = ['.txt', '.pdf', '.docx']
    document_files = []
    
    for ext in supported_extensions:
        document_files.extend(list(documents_folder.glob(f"*{ext}")))
    
    if not document_files:
        st.info("📄 No documents found in documents folder. Add documents to `data/documents/` folder and restart the app.")
        return
    
    # Load documents into knowledge base
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
            st.warning(f"⚠️ Could not load {doc_path.name}: {str(e)}")
    
    if loaded_count > 0:
        st.success(f"✅ Loaded {loaded_count} new documents into the knowledge base!")

def display_knowledge_base_status():
    """Display current knowledge base status."""
    st.markdown("### 📚 Knowledge Base Status")
    
    try:
        documents = st.session_state.knowledge_base.list_documents()
        
        if not documents:
            st.markdown("""
            <div class="info-box">
                <strong>📄 No documents loaded</strong><br>
                Add documents to the <code>data/documents/</code> folder and restart the app to populate the knowledge base.
            </div>
            """, unsafe_allow_html=True)
            return
        
        # Display documents in a nice format
        st.markdown(f"**📊 Total Documents:** {len(documents)}")
        
        # Create a DataFrame for better display
        doc_data = []
        for doc in documents:
            title = doc.get('title', doc.get('filename', 'Unknown'))
            metadata = doc.get('metadata', {})
            
            doc_data.append({
                'Document': title,
                'Type': metadata.get('file_type', 'Unknown').upper().replace('.', ''),
                'Size': f"{metadata.get('file_size', 0) / 1024:.1f} KB" if metadata.get('file_size') else 'Unknown',
                'Added': metadata.get('added_date', 'Unknown')[:10] if metadata.get('added_date') else 'Unknown'
            })
        
        if doc_data:
            df = pd.DataFrame(doc_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Add instructions for managing documents
        with st.expander("📝 How to Update Documents"):
            st.markdown("""
            **To add or update documents:**
            
            1. **Add documents** to the `data/documents/` folder in your project
            2. **Supported formats:** TXT, PDF, DOCX
            3. **Restart the app** to load new documents
            4. **Remove documents** by deleting them from the folder and restarting
            
            **Document Management Tips:**
            - Use descriptive filenames for easy identification
            - Keep documents focused on financial topics for best results
            - Organize by categories (e.g., `budgeting-guide.pdf`, `investment-basics.txt`)
            
            **Current Document Folder:** `data/documents/`
            """)
        
    except Exception as e:
        st.error(f"❌ Error displaying knowledge base status: {str(e)}")

def main():
    """Main application function."""
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>💰 Personal Finance Q&A Assistant</h1>
        <p>Get expert financial advice powered by AI and curated knowledge</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize application
    if not initialize_app():
        st.stop()
    
    # Sidebar with knowledge base status
    with st.sidebar:
        st.markdown("## 🎛️ Knowledge Base")
        display_knowledge_base_status()
        
        st.markdown("---")
        st.markdown("### ℹ️ About")
        st.markdown("""
        This app provides personalized financial advice based on curated financial documents and AI analysis.
        
        **Features:**
        - 🤖 AI-powered responses using Google Gemini
        - 📚 Curated financial knowledge base
        - 💡 Source citations for transparency
        - 📱 Mobile-friendly interface
        
        **Note:** Documents are managed by the app administrator. 
        Users cannot upload files directly.
        """)
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("## 💬 Ask Your Finance Question")
        
        # Question input
        user_question = st.text_area(
            "What would you like to know about personal finance?",
            placeholder="e.g., How should I start investing as a beginner? What's the best way to create a budget?",
            height=100,
            help="Ask specific questions about budgeting, investing, saving, debt management, or other financial topics."
        )
        
        # Submit button
        if st.button("🔍 Get Answer", type="primary"):
            if not user_question.strip():
                st.warning("📝 Please enter a question first.")
            else:
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
                    with st.spinner("🤔 Thinking and searching knowledge base..."):
                        try:
                            # Search knowledge base
                            relevant_docs = st.session_state.knowledge_base.search(user_question, top_k=3)
                            
                            # Generate response using Gemini
                            response = st.session_state.gemini_client.generate_response(
                                question=user_question,
                                context_documents=relevant_docs
                            )
                            
                            # Display response
                            st.markdown("### 💡 Answer")
                            st.markdown(response['answer'])
                            
                            # Display confidence and sources
                            if response.get('confidence'):
                                confidence_color = "🟢" if response['confidence'] > 0.7 else "🟡" if response['confidence'] > 0.4 else "🔴"
                                st.markdown(f"**Confidence:** {confidence_color} {response['confidence']:.1%}")
                            
                            if response.get('sources'):
                                st.markdown("### 📚 Sources")
                                for i, source in enumerate(response['sources'], 1):
                                    title = source.get('title', source.get('filename', f'Document {i}'))
                                    with st.expander(f"📄 Source {i}: {title}"):
                                        st.markdown(f"**Relevance Score:** {source.get('score', 0):.3f}")
                                        st.markdown("**Content:**")
                                        content = source.get('content', 'No content available')
                                        display_content = content[:500] + "..." if len(content) > 500 else content
                                        st.markdown(display_content)
                            
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
    
    with col2:
        st.markdown("## 📋 Quick Tips")
        st.markdown("""
        **💡 How to get better answers:**
        
        ✅ **Be specific**  
        "How much should I save for retirement at age 30?" vs "Tell me about retirement"
        
        ✅ **Include context**  
        "I'm 25, make $50k, want to start investing - where do I begin?"
        
        ✅ **Ask follow-ups**  
        Build on previous answers for deeper insights
        
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
        
        for question in sample_questions:
            if st.button(f"💭 {question}", key=f"sample_{hash(question)}"):
                # Set the question in session state to be picked up
                st.session_state.sample_question = question
                st.rerun()
        
        # Handle sample question selection
        if hasattr(st.session_state, 'sample_question'):
            st.text_area(
                "Selected question:",
                value=st.session_state.sample_question,
                key="sample_display",
                disabled=True
            )
            if st.button("🔍 Use This Question"):
                # Process the sample question
                user_question = st.session_state.sample_question
                delattr(st.session_state, 'sample_question')
                # Trigger processing logic here similar to the main question input

if __name__ == "__main__":
    main() 