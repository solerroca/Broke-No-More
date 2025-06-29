# Personal Finance Assistant

A Streamlit web application that provides personalized financial advice based on your own knowledge base using Google's Gemini AI.

## Features

- 🤖 **AI-Powered Q&A**: Ask questions about personal finance and get answers based on your knowledge base
- 📚 **Knowledge Base Management**: Upload and manage financial documents (PDF, DOCX, TXT)
- 🔍 **Smart Document Search**: Uses vector embeddings to find relevant information
- 🚀 **Easy Deployment**: Ready for Streamlit Cloud deployment
- 🔒 **Secure**: Uses environment variables for API keys

## Setup

### Local Development

1. **Clone and navigate to the project:**
   ```bash
   cd Proj_4_Money_Advice
   ```

2. **Install dependencies:**
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
   ```bash
   streamlit run app.py
   ```

### Streamlit Cloud Deployment

1. **Fork this repository** to your GitHub account

2. **Go to [share.streamlit.io](https://share.streamlit.io)**

3. **Deploy your app:**
   - Connect your GitHub account
   - Select this repository
   - Set the main file path: `app.py`

4. **Add secrets in Streamlit Cloud:**
   - Go to your app settings
   - Add your environment variables in the "Secrets" section:
   ```toml
   GEMINI_API_KEY = "your_actual_api_key_here"
   ```

## Usage

### Adding Knowledge Base Content

1. **Upload Documents**: Use the sidebar to upload PDF, DOCX, or TXT files
2. **Add Text Directly**: Use the text area to add financial information directly
3. **Manage Content**: View and delete existing knowledge base entries

### Asking Questions

1. Type your personal finance question in the main input field
2. The AI will search your knowledge base for relevant information
3. Get personalized answers based on your uploaded content

### Example Questions

- "What should I consider when choosing a retirement account?"
- "How much should I save for an emergency fund?"
- "What are the tax implications of selling stocks?"
- "How do I calculate my debt-to-income ratio?"

## Project Structure

```
Proj_4_Money_Advice/
├── app.py                    # Main Streamlit application
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables template
├── README.md                # This file
├── config/
│   └── settings.py          # Configuration settings
├── src/
│   ├── knowledge_base.py    # Knowledge base management
│   ├── gemini_client.py     # Gemini API integration
│   └── utils.py             # Utility functions
├── data/
│   └── knowledge_base/      # Sample financial documents
└── .streamlit/
    └── config.toml          # Streamlit configuration
```

## API Keys

### Getting a Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key to your `.env` file

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - feel free to use this project for your personal finance needs! 