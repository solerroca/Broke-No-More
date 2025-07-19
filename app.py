"""Personal Finance Assistant - No Upload Version"""

import streamlit as st
import pandas as pd
from datetime import datetime
import os
from pathlib import Path
from typing import Optional
import base64
import random

from src.gemini_client import GeminiClient
from src.knowledge_base_simple import SimpleKnowledgeBase
from src.utils import validate_finance_question, process_document
from config.settings import get_settings

# Language translations
TRANSLATIONS = {
    'en': {
        'title': 'Personal Finance Q&A Assistant',
        'subtitle': 'Get expert financial advice powered by AI and curated knowledge',
        'question_header': '💬 Ask Your Personal Finance Question',
        'question_placeholder': 'e.g., How should I start investing as a beginner? What\'s the best way to create a budget?',
        'question_help': 'Ask specific questions about budgeting, investing, saving, debt management, or other financial topics.',
        'get_answer_btn': '🔍 Get Expert Answer',
        'enter_question': '📝 Please enter a question first.',
        'not_finance': '⚠️ Not a finance question',
        'not_finance_text': 'This app is designed for personal finance questions. Please ask about topics like: budgeting, saving, investing, debt management, retirement planning, insurance, or taxes.',
        'expert_answer': '💡 Expert Answer',
        'thinking': '🤔 Thinking and analyzing your question...',
        'example_questions': '🎯 Example Questions',
        'example_subtitle': 'Click any question below to auto-fill the input field:',
        'refresh_btn': '🔄 Refresh',
        'quick_tips': '📋 Quick Tips',
        'better_answers': '💡 How to get better answers:',
        'topics_help': '📚 Topics I can help with:',
        'disclaimer': 'Disclaimer',
        'built_on': 'Built on Money Principles from',
        'questions': [
            "What's the 50/30/20 budgeting rule?",
            "How do I start an emergency fund?",
            "What's the difference between 401k and IRA?",
            "Should I pay off debt or invest first?",
            "How much house can I afford?",
            "What is compound interest and how does it work?",
            "How do I improve my credit score?",
            "What's the difference between stocks and bonds?",
            "How much should I save for retirement?",
            "What is dollar-cost averaging?",
            "Should I get a financial advisor?",
            "How do I create a budget from scratch?",
            "What's the difference between Roth and traditional IRA?",
            "How do I negotiate my salary?",
            "What insurance do I really need?"
        ],
        'tip1_title': '💡 How to get better answers:',
        'tip1_specific': '✅ **Be specific**\n"How much should I save for retirement at age 30?" vs "Tell me about retirement"',
        'tip1_context': '✅ **Include context**\n"I\'m 25, make $50k, want to start investing - where do I begin?"',
        'tip1_followup': '✅ **Ask follow-ups**\nBuild on previous answers for deeper insights',
        'tip2_title': '📚 Topics I can help with:',
        'tip2_topics': '''- 💰 Budgeting & saving strategies
- 📈 Investment basics & strategies  
- 💳 Debt management & payoff plans
- 🏠 Home buying & mortgages
- 🛡️ Insurance & protection planning
- 📊 Tax planning & optimization
- 💼 Retirement planning'''
    },
    'es': {
        'title': 'Asistente de Finanzas Personales Q&A',
        'subtitle': 'Obtén consejos financieros expertos impulsados por IA y conocimiento curado',
        'question_header': '💬 Haz Tu Pregunta de Finanzas Personales',
        'question_placeholder': 'ej., ¿Cómo debo empezar a invertir como principiante? ¿Cuál es la mejor manera de crear un presupuesto?',
        'question_help': 'Haz preguntas específicas sobre presupuesto, inversión, ahorro, gestión de deudas u otros temas financieros.',
        'get_answer_btn': '🔍 Obtener Respuesta Experta',
        'enter_question': '📝 Por favor, ingresa una pregunta primero.',
        'not_finance': '⚠️ No es una pregunta financiera',
        'not_finance_text': 'Esta aplicación está diseñada para preguntas de finanzas personales. Por favor pregunta sobre temas como: presupuesto, ahorro, inversión, gestión de deudas, planificación de jubilación, seguros o impuestos.',
        'expert_answer': '💡 Respuesta Experta',
        'thinking': '🤔 Pensando y analizando tu pregunta...',
        'example_questions': '🎯 Preguntas de Ejemplo',
        'example_subtitle': 'Haz clic en cualquier pregunta para completar automáticamente el campo:',
        'refresh_btn': '🔄 Actualizar',
        'quick_tips': '📋 Consejos Rápidos',
        'better_answers': '💡 Cómo obtener mejores respuestas:',
        'topics_help': '📚 Temas en los que puedo ayudar:',
        'disclaimer': 'Aviso Legal',
        'built_on': 'Basado en Principios Monetarios de',
        'questions': [
            "¿Qué es la regla presupuestaria 50/30/20?",
            "¿Cómo empiezo un fondo de emergencia?",
            "¿Cuál es la diferencia entre 401k e IRA?",
            "¿Debo pagar deudas o invertir primero?",
            "¿Cuánta casa puedo permitirme?",
            "¿Qué es el interés compuesto y cómo funciona?",
            "¿Cómo mejoro mi puntaje crediticio?",
            "¿Cuál es la diferencia entre acciones y bonos?",
            "¿Cuánto debo ahorrar para la jubilación?",
            "¿Qué es el promedio de costo por dólar?",
            "¿Debo conseguir un asesor financiero?",
            "¿Cómo creo un presupuesto desde cero?",
            "¿Cuál es la diferencia entre Roth e IRA tradicional?",
            "¿Cómo negocio mi salario?",
            "¿Qué seguros realmente necesito?"
        ],
        'tip1_title': '💡 Cómo obtener mejores respuestas:',
        'tip1_specific': '✅ **Sé específico**\n"¿Cuánto debo ahorrar para la jubilación a los 30 años?" vs "Háblame de jubilación"',
        'tip1_context': '✅ **Incluye contexto**\n"Tengo 25 años, gano $50k, quiero empezar a invertir - ¿por dónde empiezo?"',
        'tip1_followup': '✅ **Haz preguntas de seguimiento**\nBásate en respuestas anteriores para obtener información más profunda',
        'tip2_title': '📚 Temas en los que puedo ayudar:',
        'tip2_topics': '''- 💰 Estrategias de presupuesto y ahorro
- 📈 Conceptos básicos y estrategias de inversión
- 💳 Gestión de deudas y planes de pago
- 🏠 Compra de vivienda e hipotecas
- 🛡️ Seguros y planificación de protección
- 📊 Planificación fiscal y optimización
- 💼 Planificación de jubilación'''
    },
    'ca': {
        'title': 'Assistent de Finances Personals Q&A',
        'subtitle': 'Obté consells financers experts impulsats per IA i coneixement curat',
        'question_header': '💬 Fes la Teva Pregunta de Finances Personals',
        'question_placeholder': 'ex., Com hauria de començar a invertir com a principiant? Quina és la millor manera de crear un pressupost?',
        'question_help': 'Fes preguntes específiques sobre pressupost, inversió, estalvi, gestió de deutes o altres temes financers.',
        'get_answer_btn': '🔍 Obtenir Resposta Experta',
        'enter_question': '📝 Si us plau, introdueix una pregunta primer.',
        'not_finance': '⚠️ No és una pregunta financera',
        'not_finance_text': 'Aquesta aplicació està dissenyada per a preguntes de finances personals. Si us plau pregunta sobre temes com: pressupost, estalvi, inversió, gestió de deutes, planificació de jubilació, assegurances o impostos.',
        'expert_answer': '💡 Resposta Experta',
        'thinking': '🤔 Pensant i analitzant la teva pregunta...',
        'example_questions': '🎯 Preguntes d\'Exemple',
        'example_subtitle': 'Fes clic a qualsevol pregunta per omplir automàticament el camp:',
        'refresh_btn': '🔄 Actualitzar',
        'quick_tips': '📋 Consells Ràpids',
        'better_answers': '💡 Com obtenir millors respostes:',
        'topics_help': '📚 Temes en què puc ajudar:',
        'disclaimer': 'Avís Legal',
        'built_on': 'Basat en Principis Monetaris de',
        'questions': [
            "Què és la regla pressupostària 50/30/20?",
            "Com començo un fons d'emergència?",
            "Quina és la diferència entre 401k i IRA?",
            "He de pagar deutes o invertir primer?",
            "Quanta casa em puc permetre?",
            "Què és l'interès compost i com funciona?",
            "Com milloro la meva puntuació creditícia?",
            "Quina és la diferència entre accions i bons?",
            "Quan he d'estalviar per a la jubilació?",
            "Què és la mitjana de cost per dòlar?",
            "He de contractar un assessor financer?",
            "Com creo un pressupost des de zero?",
            "Quina és la diferència entre Roth i IRA tradicional?",
            "Com negocio el meu salari?",
            "Quines assegurances necessito realment?"
        ],
        'tip1_title': '💡 Com obtenir millors respostes:',
        'tip1_specific': '✅ **Sigues específic**\n"Quan he d\'estalviar per a la jubilació als 30 anys?" vs "Parla\'m de jubilació"',
        'tip1_context': '✅ **Inclou context**\n"Tinc 25 anys, guanyo $50k, vull començar a invertir - per on començo?"',
        'tip1_followup': '✅ **Fes preguntes de seguiment**\nBasa\'t en respostes anteriors per obtenir informació més profunda',
        'tip2_title': '📚 Temes en què puc ajudar:',
        'tip2_topics': '''- 💰 Estratègies de pressupost i estalvi
- 📈 Conceptes bàsics i estratègies d\'inversió
- 💳 Gestió de deutes i plans de pagament
- 🏠 Compra d\'habitatge i hipoteques
- 🛡️ Assegurances i planificació de protecció
- 📊 Planificació fiscal i optimització
- 💼 Planificació de jubilació'''
    }
}

def render_language_selector():
    """Render the language selector with flags in the top right corner."""
    
    # Initialize language in session state
    if 'selected_language' not in st.session_state:
        st.session_state.selected_language = 'en'
    
    # Display current language selector in top right
    current_lang = st.session_state.selected_language
    languages = {
        'en': {'flag': '🇺🇸', 'name': 'English', 'type': 'emoji'},
        'es': {'flag': '🇪🇸', 'name': 'Español', 'type': 'emoji'}, 
        'ca': {'flag': 'catalan-flag', 'name': 'Català', 'type': 'custom'}  # Custom Catalan flag
    }
    
    # Create a simple visual language indicator in top right (non-interactive for now)
    catalan_flag_data = load_custom_flag('catalan-flag') 
    
    with st.container():
        # Right-aligned flag indicator  
        col_spacer, col_indicator = st.columns([5, 1])
        
        with col_indicator:
            # Simple visual language indicator
            st.markdown(f"""
            <div style="
                text-align: right;
                padding: 8px;
                background: white;
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                margin-bottom: 16px;
            ">
                <div style="display: flex; gap: 8px; justify-content: center; align-items: center;">
                    <span style="font-size: 16px; opacity: {'1' if current_lang == 'en' else '0.3'};">🇺🇸</span>
                    <span style="font-size: 16px; opacity: {'1' if current_lang == 'ca' else '0.3'};">
                        {'<img src="' + catalan_flag_data + '" style="width: 16px; height: 12px; border-radius: 2px;">' if catalan_flag_data else '🏴'}
                    </span>
                    <span style="font-size: 16px; opacity: {'1' if current_lang == 'es' else '0.3'};">🇪🇸</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Language selection buttons (in sidebar or hidden area)
    with st.container():
        st.markdown("##### 🌍 Language / Idioma / Idioma")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # English flag display
            st.markdown("""
            <div style="text-align: center; margin-bottom: 4px; height: 32px; display: flex; align-items: center; justify-content: center;">
                <span style="font-size: 24px;">🇺🇸</span>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("English", key="lang_en_btn", use_container_width=True):
                st.session_state.selected_language = 'en'
                st.rerun()
        
        with col2:
            # Catalan flag display
            catalan_flag_data = load_custom_flag('catalan-flag')
            if catalan_flag_data:
                st.markdown(f"""
                <div style="text-align: center; margin-bottom: 4px; height: 32px; display: flex; align-items: center; justify-content: center;">
                    <img src="{catalan_flag_data}" alt="Catalan flag" style="width: 24px; height: 18px; border-radius: 2px;">
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="text-align: center; margin-bottom: 4px; height: 32px; display: flex; align-items: center; justify-content: center;">
                    <span style="font-size: 24px;">🏴</span>
                </div>
                """, unsafe_allow_html=True)
            
            if st.button("Català", key="lang_ca_btn", use_container_width=True):
                st.session_state.selected_language = 'ca'
                st.rerun()
        
        with col3:
            # Spanish flag display
            st.markdown("""
            <div style="text-align: center; margin-bottom: 4px; height: 32px; display: flex; align-items: center; justify-content: center;">
                <span style="font-size: 24px;">🇪🇸</span>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Español", key="lang_es_btn", use_container_width=True):
                st.session_state.selected_language = 'es'
                st.rerun()

def get_text(key):
    """Get translated text based on selected language."""
    lang = st.session_state.get('selected_language', 'en')
    return TRANSLATIONS.get(lang, TRANSLATIONS['en']).get(key, key)

# Page configuration
st.set_page_config(
    page_title="Personal Finance Q&A Assistant",
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
    


    /* 📱 MOBILE-FRIENDLY STYLES */
    @media (max-width: 768px) {

        
        /* Adjust main header for mobile */
        .main-header {
            padding: 1.5rem 1rem;
            margin-bottom: 1.5rem;
        }
        
        .main-header h1 {
            font-size: 1.8rem !important;
            margin-bottom: 0.5rem;
        }
        
        .main-header p {
            font-size: 0.9rem !important;
        }
        
        /* Better spacing for mobile */
        .main .block-container {
            padding-top: 1rem;
            padding-left: 1rem;
            padding-right: 1rem;
        }
        
        /* Make buttons bigger and more touch-friendly */
        .stButton > button {
            font-size: 0.9rem;
            padding: 0.8rem 1rem;
            margin-bottom: 0.5rem;
            min-height: 48px; /* Good for touch screens */
        }
        
        /* Improve text readability on mobile */
        .stMarkdown {
            font-size: 1rem;
        }
        
        /* Better spacing for info boxes */
        .info-box, .warning-box, .success-box {
            padding: 1rem;
            margin: 1rem 0;
        }
        
        /* Make promotional book image smaller on mobile */
        .mobile-book-promo img {
            max-width: 200px !important;
            height: auto;
        }
        
        /* Make book promotional section mobile-friendly */
        .main-header + div img {
            max-width: 200px !important;
        }
    }
    
    /* 📱 TABLET STYLES (medium screens) */
    @media (min-width: 769px) and (max-width: 1024px) {
        .main .block-container {
            padding-left: 2rem;
            padding-right: 2rem;
        }
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

def load_custom_flag(flag_name):
    """Load and encode a custom flag image."""
    try:
        # Try PNG first (better browser support), then SVG
        for ext in ['.png', '.svg']:
            flag_path = Path(f"static/images/flags/{flag_name}{ext}")
            if flag_path.exists():
                with open(flag_path, "rb") as flag_file:
                    flag_data = base64.b64encode(flag_file.read()).decode()
                    file_type = "svg+xml" if ext == '.svg' else "png"
                    return f"data:image/{file_type};base64,{flag_data}"
        return None
    except Exception as e:
        print(f"⚠️ Error loading flag {flag_name}: {e}")
        return None

def main():
    """Main application function."""
    
    # Language selector
    render_language_selector()
    
    # Header with translations
    title = get_text('title')
    subtitle = get_text('subtitle')
    
    st.markdown(f"""
    <div class="main-header">
        <h1>💰 {title}</h1>
        <p>{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Promotional section for "Broke No More" book
    book_image_data = load_book_image()
    
    if book_image_data:
        # Show promotional section with professional styling - entire section is clickable
        st.markdown(f"""
        <div style="text-align: center; margin: 30px 0;">
            <div style="margin-bottom: 10px;">
                <p style="color: #2c3e50; font-size: 1.1em; font-weight: 700; margin: 0;">{get_text('built_on')}</p>
            </div>
            <a href="https://www.amazon.com/Broke-More-Easy-Follow-Strategies/dp/196628800X/ref=sr_1_2?crid=1I2229DFKOWE2&dib=eyJ2IjoiMSJ9.Y3EC7BYPotcNcCpQkFuWgyTURtZXDgSMa7v87YOnt6xEb5zqzgwRhigftpmGRMm4li93dXytUd--woy-3Rgy2IyLVY6WKfoqkPhv2wCyF6Hfw0BtnlDDAko1UEaUoucVe6Xkm91djx57Bhqy8Dzs2eNZKDL91bhxdBCwFUA-rQUqzyTIp7oB0OG_dWcP4nj1xEcm0eVBjM4sSSdmHdwiq2BQAFp1p9_rLQWo2z-n0_M.ogRhG6GClaDbNPhSUSXTVFswk4_0KRCJLAb9iR8n0S4&dib_tag=se&keywords=broke+no+more&qid=1751304047&sprefix=broke+no+more%2Caps%2C171&sr=8-2" target="_blank" style="text-decoration: none; display: block;">
                <div style="display: inline-block; background: white; padding: 20px; border-radius: 12px; box-shadow: 0 2px 15px rgba(0,0,0,0.08); transition: transform 0.2s ease, box-shadow 0.2s ease;" onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 4px 25px rgba(0,0,0,0.12)'" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 2px 15px rgba(0,0,0,0.08)'">
                    <img src="data:image/png;base64,{book_image_data}" alt="Broke No More - The Gen Z Guide to Money Mastery" style="max-width: 280px; height: auto; border-radius: 8px;" class="responsive-book-img">
                    <div style="margin-top: 12px;">
                        <h3 style="color: #2c3e50; margin: 0; font-size: 1.2em; font-weight: 600;">'Broke No More'</h3>
                        <p style="color: #7f8c8d; margin: 4px 0 0 0; font-size: 0.9em;">📚 Link to the book</p>
                    </div>
                </div>
            </a>
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
    st.markdown(f"## {get_text('question_header')}")
    
    # Initialize selected question in session state
    if 'selected_question' not in st.session_state:
        st.session_state.selected_question = ""
    
    # Question input with translations
    user_question = st.text_area(
        label="Your Finance Question",
        value=st.session_state.selected_question,
        placeholder=get_text('question_placeholder'),
        height=120,
        help=get_text('question_help'),
        label_visibility="collapsed"
    )
    
    # Submit button - fixed size and centered
    st.markdown("""
    <style>
        .stButton > button[kind="primary"] {
            width: 300px !important;
            height: 70px !important;
            font-size: 22px !important;
            font-weight: 800 !important;
            border-radius: 8px !important;
            background-color: #ff4b4b !important;
            border-color: #ff4b4b !important;
        }
        .stButton > button[kind="primary"]:hover {
            background-color: #ff6b6b !important;
            border-color: #ff6b6b !important;
        }
        .main-button-container {
            display: flex;
            justify-content: center;
            align-items: center;
            margin: 30px 0;
            width: 100%;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Center the button using columns but handle response outside columns
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        button_clicked = st.button(get_text('get_answer_btn'), type="primary", key="expert_answer_btn")
    
    # Handle button response outside of column context for full-width display
    if button_clicked:
        if not user_question.strip():
            st.warning(get_text('enter_question'))
        else:
            # Clear the selected question from session state
            st.session_state.selected_question = ""
            
            # Validate if it's a finance-related question
            if not validate_finance_question(user_question):
                st.markdown(f"""
                <div class="warning-box">
                    <strong>{get_text('not_finance')}</strong><br>
                    {get_text('not_finance_text')}
                </div>
                """, unsafe_allow_html=True)
            else:
                # Process the question
                with st.spinner(get_text('thinking')):
                    try:
                        # Search knowledge base
                        relevant_docs = st.session_state.knowledge_base.search(user_question, top_k=3)
                        
                        # Generate response using Gemini with language preference
                        response = st.session_state.gemini_client.generate_response(
                            question=user_question,
                            context_documents=relevant_docs,
                            language=st.session_state.selected_language
                        )
                        
                        # Display response - clean format without confidence or sources
                        st.markdown(f"### {get_text('expert_answer')}")
                        
                        # Apply consistent CSS styling for the answer
                        st.markdown("""
                        <style>
                        .expert-answer {
                            font-family: 'Source Sans Pro', sans-serif;
                            font-size: 16px !important;
                            line-height: 1.6;
                            color: #262730;
                            background-color: #ffffff;
                            padding: 20px;
                            border-radius: 8px;
                            border: 1px solid #e6e6e6;
                        }
                        .expert-answer p {
                            font-size: 16px !important;
                            margin: 16px 0 !important;
                            font-weight: 400 !important;
                        }
                        .expert-answer strong, .expert-answer b {
                            font-weight: 600 !important;
                            font-size: 16px !important;
                        }
                        .expert-answer em, .expert-answer i {
                            font-style: italic !important;
                            font-size: 16px !important;
                            font-weight: 400 !important;
                        }
                        .expert-answer ul, .expert-answer ol {
                            margin: 16px 0 !important;
                            padding-left: 20px !important;
                        }
                        .expert-answer li {
                            font-size: 16px !important;
                            margin: 6px 0 !important;
                            font-weight: 400 !important;
                            line-height: 1.5;
                        }
                        /* Make subheaders visually distinct but proportional */
                        .expert-answer h1 {
                            font-size: 20px !important;
                            font-weight: 700 !important;
                            margin: 24px 0 12px 0 !important;
                            color: #1e3a8a !important;
                            border-bottom: 2px solid #e6e6e6 !important;
                            padding-bottom: 8px !important;
                        }
                        .expert-answer h2 {
                            font-size: 18px !important;
                            font-weight: 600 !important;
                            margin: 20px 0 10px 0 !important;
                            color: #1e40af !important;
                        }
                        .expert-answer h3 {
                            font-size: 16px !important;
                            font-weight: 600 !important;
                            margin: 16px 0 8px 0 !important;
                            color: #3b82f6 !important;
                        }
                        .expert-answer h4, .expert-answer h5, .expert-answer h6 {
                            font-size: 16px !important;
                            font-weight: 600 !important;
                            margin: 16px 0 8px 0 !important;
                            color: #64748b !important;
                        }
                        </style>
                        """, unsafe_allow_html=True)
                        
                        # Process markdown to HTML for proper header rendering
                        import re
                        
                        def convert_markdown_to_html(text):
                            try:
                                # Try using markdown library if available
                                import markdown
                                html = markdown.markdown(text)
                                return html
                            except ImportError:
                                # Fallback to simple regex conversion
                                # Convert markdown headers to HTML headers
                                text = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
                                text = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
                                text = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)
                                
                                # Convert markdown lists to HTML lists
                                lines = text.split('\n')
                                html_lines = []
                                in_list = False
                                
                                for line in lines:
                                    if line.strip().startswith('•') or line.strip().startswith('-'):
                                        if not in_list:
                                            html_lines.append('<ul>')
                                            in_list = True
                                        item_text = line.strip()[1:].strip()
                                        html_lines.append(f'<li>{item_text}</li>')
                                    else:
                                        if in_list:
                                            html_lines.append('</ul>')
                                            in_list = False
                                        if line.strip() and not line.strip().startswith('<'):
                                            html_lines.append(f'<p>{line.strip()}</p>')
                                        else:
                                            html_lines.append(line)
                                
                                if in_list:
                                    html_lines.append('</ul>')
                                
                                return '\n'.join(html_lines)
                        
                        # Convert markdown to HTML
                        final_answer = convert_markdown_to_html(response['answer'])
                        
                        st.markdown(f'<div class="expert-answer">{final_answer}</div>', unsafe_allow_html=True)
                        
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
    
    # Sample questions - moved above tips
    st.markdown("---")
    
    st.markdown(f"### {get_text('example_questions')}")
    st.markdown(get_text('example_subtitle'))
    
    # Get questions in current language
    all_questions = get_text('questions')
    
    # Check if language changed and update questions accordingly
    current_lang = st.session_state.get('selected_language', 'en')
    if 'questions_language' not in st.session_state:
        st.session_state.questions_language = current_lang
    
    # If language changed, update the questions
    if st.session_state.questions_language != current_lang:
        st.session_state.questions_language = current_lang
        st.session_state.current_sample_questions = random.sample(all_questions, 5)
    
    # Refresh button below the heading
    if st.button(get_text('refresh_btn'), help="Get new example questions", key="refresh_questions", type="secondary"):
        st.session_state.current_sample_questions = random.sample(all_questions, 5)
        st.rerun()
    
    # Randomly select 5 questions to display (initialize if needed)
    if 'current_sample_questions' not in st.session_state:
        st.session_state.current_sample_questions = random.sample(all_questions, 5)
    
    sample_questions = st.session_state.current_sample_questions
    
    # Display sample questions in mobile-friendly layout
    # Create a responsive grid that works well on both mobile and desktop
    
    # On mobile: 1 column, on desktop: 2 columns per row
    if len(sample_questions) >= 4:
        # Create mobile-friendly rows
        for i in range(0, len(sample_questions), 2):
            row_cols = st.columns(2)
            for j, col in enumerate(row_cols):
                if i + j < len(sample_questions):
                    question = sample_questions[i + j]
                    button_key = f"sample_{i + j}"
                    with col:
                        if st.button(f"💭 {question}", key=button_key, type="secondary", use_container_width=True):
                            st.session_state.selected_question = question
                            st.rerun()
    else:
        # For fewer questions, use regular column layout
        cols = st.columns(len(sample_questions))
        for i, question in enumerate(sample_questions):
            with cols[i]:
                if st.button(f"💭 {question}", key=f"sample_{i}", type="secondary", use_container_width=True):
                    st.session_state.selected_question = question
                    st.rerun()
    
    # Tips section
    st.markdown("---")
    st.markdown(f"## {get_text('quick_tips')}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        **{get_text('tip1_title')}**
        
        {get_text('tip1_specific')}
        
        {get_text('tip1_context')}
        
        {get_text('tip1_followup')}
        """)
    
    with col2:
        st.markdown(f"""
        **{get_text('tip2_title')}**
        {get_text('tip2_topics')}
        """)
    
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