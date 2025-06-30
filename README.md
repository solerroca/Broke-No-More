# Personal Finance Assistant

A streamlined Streamlit web application that provides personalized financial advice using Google's Gemini AI and a curated knowledge base of financial documents.

## Features

- 🤖 **AI-Powered Q&A**: Ask questions about personal finance and get expert answers
- 📚 **Curated Knowledge Base**: Pre-loaded with comprehensive financial guides
- 🔍 **Smart Document Search**: Uses text search to find relevant information
- 💰 **Expert Financial Advice**: AI responds as a Certified Financial Planner with 20+ years experience
- 🚀 **Easy Deployment**: Ready for Streamlit Cloud deployment
- 🔒 **Secure**: Administrator-controlled content, protected API keys
- 📱 **Mobile-Friendly**: Clean, responsive interface

## Pre-loaded Financial Content

The app comes with expert-curated guides covering:

- **📊 Budgeting Basics**: 50/30/20 rule, budgeting strategies, emergency funds
- **📈 Investment Fundamentals**: Stocks, bonds, index funds, asset allocation, retirement accounts
- **💳 Debt Management**: Payoff strategies, credit optimization, loan management
- **🏠 Retirement Planning**: 401k, IRA, Social Security, retirement strategies

## Setup

### Local Development

1. **Clone and navigate to the project:**
   ```bash
   cd Proj_4_Money_Advice
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv finance_assistant_env
   source finance_assistant_env/bin/activate  # On Windows: finance_assistant_env\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements-light.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and add your Gemini API key:
   ```
   GEMINI_API_KEY=your_actual_api_key_here
   GEMINI_MODEL=gemini-1.5-flash
   ```

5. **Run the application:**
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
   GEMINI_MODEL = "gemini-1.5-flash"
   ```

## Usage

### Asking Questions

1. Type your personal finance question in the main input field
2. Click "Get Expert Answer" to receive personalized advice
3. The AI responds as an experienced financial advisor with warm, educational tone

### Example Questions

- "What's the 50/30/20 budgeting rule and how do I use it?"
- "How should I start investing as a beginner?"
- "What's the difference between debt snowball and avalanche methods?"
- "How much should I save for an emergency fund?"
- "Should I pay off debt or invest first?"
- "What's the best retirement account for someone in their 20s?"

## Knowledge Base Management (Administrator Only)

**Adding New Documents:**
1. Add documents to the `data/documents/` folder
2. Supported formats: PDF (`.pdf`), Word (`.docx`), Text (`.txt`)
3. Restart the application to load new documents
4. Documents are automatically processed and indexed

**Current Documents:**
- `budgeting-basics.txt` - Complete budgeting guide
- `investment-basics.txt` - Investment fundamentals
- `debt-management.txt` - Debt payoff strategies
- `retirement-planning.txt` - Retirement planning guide

**Why No User Uploads?**
- Ensures high-quality, accurate financial information
- Maintains consistency and reliability
- Prevents misinformation or biased content
- Simplifies deployment and maintenance

## Project Structure

```
Proj_4_Money_Advice/
├── app.py                   # Main application
├── requirements-light.txt   # Lightweight dependencies
├── .env.example            # Environment variables template
├── README.md               # This file
├── config/
│   └── settings.py         # Configuration settings
├── src/
│   ├── knowledge_base_simple.py # Text-based knowledge base
│   ├── gemini_client.py    # Gemini API integration
│   └── utils.py            # Utility functions
├── data/
│   ├── documents/          # Curated financial documents (administrator-managed)
│   │   ├── budgeting-basics.txt
│   │   ├── investment-basics.txt
│   │   ├── debt-management.txt
│   │   └── retirement-planning.txt
│   └── knowledge_base/     # JSON storage for processed documents
│       └── knowledge_base.json
└── .streamlit/
    └── config.toml         # Streamlit configuration
```

## Technical Features

- **Lightweight Architecture**: Minimal dependencies for fast deployment
- **Text-Based Search**: Efficient keyword matching for document retrieval
- **Expert AI Responses**: Gemini AI configured to respond as experienced CFP
- **Administrator Content Control**: Secure, curated financial information
- **Mobile-Responsive Design**: Works perfectly on all devices
- **Environment-Based Configuration**: Secure API key management

## API Keys

### Getting a Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key to your `.env` file

**Cost**: Gemini API has a generous free tier suitable for personal use.

## Troubleshooting

**Common Issues:**
- **Import errors**: Make sure you're in the activated virtual environment
- **API errors**: Check that your Gemini API key is valid and properly set
- **Missing documents**: Ensure documents are in the `data/documents/` folder
- **Model not found**: Update to `gemini-1.5-flash` in your environment variables

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - feel free to use this project for your personal finance needs! 