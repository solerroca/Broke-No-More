# Personal Finance Assistant

A Streamlit web application that provides personalized financial advice using Google's Gemini AI and a curated knowledge base of financial documents.

## Features

- 🤖 **AI-Powered Q&A**: Ask questions about personal finance and get expert answers
- 📚 **Curated Knowledge Base**: Pre-loaded with comprehensive financial guides
- 🔍 **Smart Document Search**: Uses text search to find relevant information
- 💡 **Source Citations**: See which documents were used for each answer
- 🚀 **Easy Deployment**: Ready for Streamlit Cloud deployment
- 🔒 **Secure**: Administrator-controlled content, protected API keys

## Pre-loaded Financial Content

The app comes with expert-curated guides covering:

- **📊 Budgeting Basics**: 50/30/20 rule, budgeting strategies, emergency funds
- **📈 Investment Fundamentals**: Stocks, bonds, index funds, asset allocation, retirement accounts
- **💳 Debt Management**: Payoff strategies, credit optimization, loan management

## Setup

### Local Development

1. **Clone and navigate to the project:**
   ```bash
   cd Proj_4_Money_Advice
   ```

2. **Install dependencies:**
   
   For the simplified version (recommended):
   ```bash
   pip install -r requirements-light.txt
   ```
   
   For the full version with vector search:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and add your Gemini API key:
   ```
   GEMINI_API_KEY=your_actual_api_key_here
   ```

4. **Run the application:**
   
   Simplified version:
   ```bash
   streamlit run app_simple.py
   ```
   
   Full version:
   ```bash
   streamlit run app.py
   ```

### Streamlit Cloud Deployment

1. **Fork this repository** to your GitHub account

2. **Go to [share.streamlit.io](https://share.streamlit.io)**

3. **Deploy your app:**
   - Connect your GitHub account
   - Select this repository
   - Set the main file path: `app_simple.py` (recommended) or `app.py`

4. **Add secrets in Streamlit Cloud:**
   - Go to your app settings
   - Add your environment variables in the "Secrets" section:
   ```toml
   GEMINI_API_KEY = "your_actual_api_key_here"
   ```

## Usage

### Asking Questions

1. Type your personal finance question in the main input field
2. The AI searches the curated knowledge base for relevant information
3. Get expert answers with source citations

### Example Questions

- "What's the 50/30/20 budgeting rule and how do I use it?"
- "How should I start investing as a beginner?"
- "What's the difference between debt snowball and avalanche methods?"
- "How much should I save for an emergency fund?"
- "Should I pay off debt or invest first?"

## Knowledge Base Management (Administrator Only)

**Adding New Documents:**
1. Add documents to the `data/documents/` folder
2. Supported formats: PDF (`.pdf`), Word (`.docx`), Text (`.txt`)
3. Restart the application to load new documents
4. Documents are automatically processed and indexed

**Why No User Uploads?**
- Ensures high-quality, accurate financial information
- Maintains consistency and reliability
- Prevents misinformation or biased content
- Simplifies deployment and maintenance

## Project Structure

```
Proj_4_Money_Advice/
├── app.py                    # Full version with vector search
├── app_simple.py            # Simplified version (recommended)
├── requirements.txt          # Full dependencies
├── requirements-light.txt    # Lightweight dependencies
├── .env.example             # Environment variables template
├── README.md                # This file
├── config/
│   └── settings.py          # Configuration settings
├── src/
│   ├── knowledge_base.py    # Vector-based knowledge base
│   ├── knowledge_base_simple.py # Simple text-based search
│   ├── gemini_client.py     # Gemini API integration
│   └── utils.py             # Utility functions
├── data/
│   ├── documents/           # Curated financial documents
│   │   ├── budgeting-basics.txt
│   │   ├── investment-basics.txt
│   │   └── debt-management.txt
│   ├── chroma_db/          # Vector database (full version)
│   └── knowledge_base/     # JSON storage (simple version)
└── .streamlit/
    └── config.toml          # Streamlit configuration
```

## Two Versions Available

### Simple Version (`app_simple.py`) - Recommended
- Lightweight dependencies
- Text-based search
- Faster deployment
- Perfect for most use cases

### Full Version (`app.py`)
- Advanced vector search with ChromaDB
- Semantic similarity matching
- More dependencies
- Better for complex queries

## API Keys

### Getting a Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key to your `.env` file

**Cost**: Gemini API has a generous free tier suitable for personal use.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - feel free to use this project for your personal finance needs! 