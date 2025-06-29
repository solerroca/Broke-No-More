"""Personal Finance Assistant - Main Streamlit Application"""

import streamlit as st
import os
from typing import Optional
from config.settings import settings
from src.knowledge_base import get_knowledge_base
from src.gemini_client import get_gemini_client
from src.utils import (
    create_directories, 
    extract_text_from_file, 
    validate_finance_question,
    format_response,
    get_file_size_mb
)


def initialize_app():
    """Initialize the Streamlit app configuration."""
    st.set_page_config(
        page_title=settings.PAGE_TITLE,
        page_icon=settings.PAGE_ICON,
        layout=settings.LAYOUT,
        initial_sidebar_state="expanded"
    )
    
    # Create necessary directories
    create_directories()
    
    # Initialize session state
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'knowledge_base_initialized' not in st.session_state:
        st.session_state.knowledge_base_initialized = False


def check_api_setup() -> bool:
    """Check if the API is properly configured."""
    if not settings.validate_api_key():
        st.error("🚨 **Gemini API Key Required**")
        st.markdown("""
        Please set up your Gemini API key:
        
        **For local development:**
        1. Copy `.env.example` to `.env`
        2. Add your Gemini API key to the `.env` file
        
        **For Streamlit Cloud:**
        1. Go to your app settings
        2. Add `GEMINI_API_KEY` in the Secrets section
        
        **Get your API key:** [Google AI Studio](https://makersuite.google.com/app/apikey)
        """)
        return False
    return True


def display_header():
    """Display the app header and description."""
    st.title("💰 Personal Finance Assistant")
    st.markdown("""
    Ask questions about personal finance and get answers based on your custom knowledge base.
    Upload financial documents or add text directly to build your personalized financial advisor.
    """)


def display_sidebar():
    """Display the sidebar with knowledge base management."""
    with st.sidebar:
        st.header("📚 Knowledge Base")
        
        # Initialize knowledge base
        kb = get_knowledge_base()
        
        # Display stats
        stats = kb.get_stats()
        st.metric("Documents", stats['total_documents'])
        st.metric("Text Chunks", stats['total_chunks'])
        
        # File upload section
        st.subheader("📁 Upload Documents")
        uploaded_files = st.file_uploader(
            "Upload financial documents",
            **settings.get_file_upload_config()
        )
        
        if uploaded_files:
            for uploaded_file in uploaded_files:
                if st.button(f"Add {uploaded_file.name}", key=f"add_{uploaded_file.name}"):
                    # Check file size
                    file_content = uploaded_file.read()
                    file_size_mb = get_file_size_mb(file_content)
                    
                    if file_size_mb > settings.MAX_FILE_SIZE_MB:
                        st.error(f"File too large: {file_size_mb:.1f}MB (max: {settings.MAX_FILE_SIZE_MB}MB)")
                        continue
                    
                    # Reset file pointer
                    uploaded_file.seek(0)
                    
                    # Extract text
                    text_content = extract_text_from_file(uploaded_file)
                    if text_content:
                        # Add to knowledge base
                        file_type = os.path.splitext(uploaded_file.name)[1][1:]  # Remove dot
                        kb.add_document(text_content, uploaded_file.name, file_type)
                        st.rerun()
        
        # Text input section
        st.subheader("✍️ Add Text Directly")
        with st.form("add_text_form"):
            text_title = st.text_input("Title/Description")
            text_content = st.text_area("Financial Information", height=150)
            
            if st.form_submit_button("Add Text"):
                if text_content.strip() and text_title.strip():
                    kb.add_document(text_content, text_title, "text")
                    st.rerun()
                else:
                    st.error("Please provide both title and content")
        
        # Knowledge base management
        st.subheader("🗂️ Manage Documents")
        
        all_docs = kb.get_all_documents()
        if all_docs:
            for doc in all_docs:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.text(f"📄 {doc['filename']}")
                    st.caption(f"Type: {doc['file_type']} | Chunks: {doc.get('total_chunks', 1)}")
                with col2:
                    if st.button("🗑️", key=f"delete_{doc['doc_hash']}", help="Delete document"):
                        kb.delete_document(doc['doc_hash'])
                        st.rerun()
            
            # Clear all button
            st.divider()
            if st.button("🗑️ Clear All Documents", type="secondary"):
                if st.session_state.get('confirm_clear', False):
                    kb.clear_all()
                    st.session_state.confirm_clear = False
                    st.rerun()
                else:
                    st.session_state.confirm_clear = True
                    st.warning("Click again to confirm clearing all documents")
        else:
            st.info("No documents in knowledge base. Upload some documents to get started!")


def display_chat_interface():
    """Display the main chat interface."""
    # Initialize clients
    kb = get_knowledge_base()
    gemini_client = get_gemini_client()
    
    if gemini_client is None:
        st.error("Failed to initialize Gemini client. Please check your API key.")
        return
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Show sources for assistant messages
            if message["role"] == "assistant" and "sources" in message:
                with st.expander("📖 Sources Used"):
                    for i, source in enumerate(message["sources"], 1):
                        st.write(f"**{i}. {source['filename']}** (similarity: {source['similarity']:.2f})")
                        st.write(f"_{source['content'][:200]}..._")
    
    # Chat input
    if prompt := st.chat_input("Ask a question about personal finance..."):
        # Validate question
        if not validate_finance_question(prompt):
            st.warning("⚠️ This appears to be a non-finance question. This assistant is designed to help with personal finance topics.")
            return
        
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Searching knowledge base and generating response..."):
                # Search for relevant documents
                relevant_docs = kb.search_documents(prompt)
                
                if not relevant_docs:
                    response = "I couldn't find relevant information in your knowledge base to answer this question. Please add more financial documents or information to help me provide better answers."
                    sources = []
                else:
                    # Extract document content for context
                    context_docs = [doc['content'] for doc in relevant_docs]
                    
                    # Generate response using Gemini
                    response = gemini_client.generate_response(prompt, context_docs)
                    sources = relevant_docs
                    
                    if not response:
                        response = "I'm sorry, I encountered an error while generating a response. Please try again."
                        sources = []
                
                # Format and display response
                formatted_response = format_response(response)
                st.markdown(formatted_response)
                
                # Show sources
                if sources:
                    with st.expander("📖 Sources Used"):
                        for i, source in enumerate(sources, 1):
                            st.write(f"**{i}. {source['filename']}** (similarity: {source['similarity']:.2f})")
                            st.write(f"_{source['content'][:200]}..._")
        
        # Add assistant response to chat
        assistant_message = {
            "role": "assistant", 
            "content": formatted_response
        }
        if sources:
            assistant_message["sources"] = sources
        
        st.session_state.messages.append(assistant_message)


def display_help_section():
    """Display help and example questions."""
    with st.expander("❓ Help & Example Questions"):
        st.markdown("""
        ### How to Use This App:
        1. **Add Documents**: Upload PDF, DOCX, or TXT files with financial information
        2. **Add Text**: Directly input financial advice or information
        3. **Ask Questions**: Type your personal finance questions in the chat
        
        ### Example Questions:
        - "How much should I save for an emergency fund?"
        - "What's the difference between a Roth IRA and traditional IRA?"
        - "How should I prioritize paying off debt?"
        - "What percentage of income should go to retirement savings?"
        - "What types of insurance do I need?"
        
        ### Tips:
        - Be specific in your questions for better answers
        - Add comprehensive financial documents for more detailed responses
        - The AI will only use information from your knowledge base
        """)


def main():
    """Main application function."""
    # Initialize app
    initialize_app()
    
    # Check API setup
    if not check_api_setup():
        return
    
    # Display header
    display_header()
    
    # Display sidebar
    display_sidebar()
    
    # Display help section
    display_help_section()
    
    # Display main chat interface
    display_chat_interface()
    
    # Footer
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: gray;'>
        Personal Finance Assistant | Built with Streamlit & Gemini AI
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main() 