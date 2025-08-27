# 📈 Financial AI Agent

*An intelligent financial research assistant powered by Google Gemini, offering comprehensive stock analysis, sentiment insights, and market intelligence through an intuitive Gradio interface.*

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Gradio](https://img.shields.io/badge/Interface-Gradio-orange.svg)](https://gradio.app/)
[![LangChain](https://img.shields.io/badge/Powered%20by-LangChain-yellow.svg)](https://langchain.com/)

---

## 🌟 Overview

The **Financial AI Agent** is a sophisticated financial research platform that leverages advanced AI technologies to provide real-time market insights, sentiment analysis, and comprehensive stock research. Built with Google's Gemini AI model and an extensive toolkit of financial data sources, this application transforms complex financial queries into actionable intelligence.

### ✨ Key Capabilities

- 📊 **Real-time Stock Data** - Live market prices, metrics, and historical performance
- 📰 **Sentiment Analysis** - Multi-regional news sentiment tracking with NLTK VADER
- 🔍 **Intelligent Search** - Web research with DuckDuckGo integration
- 📚 **Knowledge Base** - Wikipedia integration for company background
- 🎯 **Market Movers** - Live tracking of top gainers and losers
- 🎤 **Voice Interface** - Speech-to-text query processing
- 💾 **Research Memory** - Vector-based storage for past research retrieval
- 🌐 **Interactive UI** - Beautiful Gradio interface with 3D visualizations

---

## 🏗️ Technical Architecture

### 🔧 Technology Stack

| Component | Technology | Purpose |
|-----------|------------|----------|
| **AI Model** | Google Gemini 2.5-Flash | Core reasoning and response generation |
| **Framework** | LangChain | Agent orchestration and tool management |
| **Interface** | Gradio | Web-based user interface |
| **Stock Data** | yfinance | Real-time financial market data |
| **Web Search** | DuckDuckGo | News and web content retrieval |
| **Sentiment** | NLTK VADER | Multi-language sentiment analysis |
| **Vector DB** | ChromaDB | Research storage and similarity search |
| **Embeddings** | HuggingFace Transformers | Text vectorization |
| **Speech** | Google Speech Recognition | Voice input processing |

### 📁 Project Structure

```
Financial.AI.Agent/
├── 📄 app.py              # Gradio web interface & UI components
├── 🧠 main.py             # Core agent logic & orchestration
├── 🛠️ tools.py            # Financial analysis tools
├── 🗄️ vector.py           # Vector storage & retrieval system
├── 📋 requirements.txt    # Python dependencies
├── 🙈 .gitignore          # Git ignore patterns
└── 📖 README.md           # Project documentation
```

---

## 📄 File Breakdown

### 🎨 `app.py` - User Interface Layer
**Core Functions:**
- `run_interface()` - Main Gradio interface handler
- Processes text and audio inputs
- Formats AI responses for display
- Implements 3D particle background with Three.js
- Custom CSS styling for dark theme

**UI Components:**
- Text input for financial queries
- Microphone integration for voice queries
- Tabbed results display (Stock Data, Research, Extra Info)
- Real-time processing feedback

### 🧠 `main.py` - Agent Intelligence Core
**Key Components:**
- `validate_google_api_key()` - API key validation
- `transcribe_audio()` - Speech-to-text conversion
- `process_query()` - Main query processing pipeline
- Agent executor with tool integration
- Structured response formatting with Pydantic

**AI Agent Features:**
- Intelligent tool selection based on query type
- Multi-step reasoning and analysis
- Research storage and retrieval
- Error handling and recovery

### 🛠️ `tools.py` - Financial Analysis Toolkit
**Available Tools:**

1. **`stock_tool(symbol)`**
   - Fetches comprehensive stock data via yfinance
   - Returns: price, market cap, daily high/low, previous close
   - Input validation and error handling

2. **`search_tool(query)`**
   - Web search using DuckDuckGo
   - Returns recent news and analysis
   - Multi-regional search capability

3. **`wiki_tool(query)`**
   - Wikipedia integration for company backgrounds
   - Structured knowledge retrieval
   - Content summarization

4. **`sentiment_tool(company_name)`**
   - Multi-regional news sentiment analysis
   - NLTK VADER sentiment scoring
   - Aggregated sentiment metrics across regions

5. **`get_live_market_movers_tool(industry)`**
   - Real-time top gainers and losers
   - Industry-specific filtering
   - Percentage change calculations

### 🗄️ `vector.py` - Memory & Knowledge Base
**Functions:**
- `get_vector_store()` - ChromaDB initialization with HuggingFace embeddings
- `store_research_response()` - Save AI research for future reference
- `retrieve_similar_docs()` - Find related past research

**Features:**
- Persistent vector storage
- Semantic similarity search
- Research history tracking
- Metadata-rich document storage

---

## ⚙️ Configuration & Setup

### 📋 Prerequisites
- Python 3.8 or higher
- Google AI API key (Gemini)
- Optional: FMP (Financial Modeling Prep) API key for enhanced market data

### 🔧 Environment Variables
Create a `.env` file in the project root:

```env
# Required: Google AI API Key for Gemini
GOOGLE_API_KEY=your_google_api_key_here

# Optional: Financial Modeling Prep API Key
FMP_API_KEY=your_fmp_api_key_here
```

### 📦 Installation Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/rah-9/Financial.AI.Agent.git
   cd Financial.AI.Agent
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv financial-ai-env
   source financial-ai-env/bin/activate  # On Windows: financial-ai-env\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

5. **Initialize NLTK data (first run only):**
   ```python
   python -c "import nltk; nltk.download('vader_lexicon')"
   ```

---

## 🚀 Usage Instructions

### 💻 Running the Application

**Start the Gradio interface:**
```bash
python app.py
```

**Access the web interface:**
- Local: `http://localhost:7860`
- The interface will automatically open in your default browser

### 📝 Query Examples

**Stock Analysis:**
```
"What is the current stock price and performance of Apple?"
"Analyze Tesla's recent stock data and market cap"
"Show me Microsoft's daily trading range"
```

**Market Intelligence:**
```
"What are today's top gaining stocks?"
"Show me the worst performing technology stocks"
"Find the top market movers in the healthcare sector"
```

**Sentiment Analysis:**
```
"What's the current sentiment around NVIDIA in the news?"
"Analyze recent news sentiment for Amazon stock"
"How is the market reacting to Google's latest earnings?"
```

**Research Queries:**
```
"Tell me about Shopify's business model and recent performance"
"Compare the financial health of Netflix vs Disney"
"What are analysts saying about the current crypto market?"
```

### 🎤 Voice Interface
1. Click the microphone icon in the interface
2. Speak your financial question clearly
3. The system will transcribe and process your query
4. Results appear in the structured format below

### 📊 Understanding Results

The application provides results in organized tabs:

- **📝 Summary**: AI-generated analysis and insights
- **📊 Key Data**: Structured JSON data with metrics
- **📚 Similar Research**: Related past research from memory
- **ℹ️ Extra Info**: Additional context (Wikipedia, tool outputs)

---

## 🛡️ Error Handling & Troubleshooting

### Common Issues

**API Key Errors:**
```
❌ GOOGLE_API_KEY not found. Please add it to your .env file.
```
*Solution: Ensure your .env file contains a valid Google API key*

**Stock Symbol Errors:**
```
❌ Invalid stock symbol format: 'XYZ'
```
*Solution: Use valid ticker symbols (e.g., AAPL, MSFT, GOOGL)*

**Audio Processing Errors:**
```
❌ Could not understand the audio
```
*Solution: Speak clearly, ensure microphone access, check audio quality*

### 🔧 Debugging Mode
Run with verbose logging:
```bash
python app.py --debug
```

---

## 🤝 Contributing

We welcome contributions! Here's how to get involved:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** with proper testing
4. **Commit changes**: `git commit -m 'Add amazing feature'`
5. **Push to branch**: `git push origin feature/amazing-feature`
6. **Open a Pull Request** with detailed description

### 📝 Development Guidelines
- Follow PEP 8 style guidelines
- Add docstrings to new functions
- Include error handling for external API calls
- Test with various input formats
- Update documentation for new features

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Google AI** for Gemini API access
- **LangChain** for the agent framework
- **Gradio** for the beautiful web interface
- **yfinance** for reliable stock data
- **Hugging Face** for embedding models
- **ChromaDB** for vector storage capabilities

---

## 📞 Support

Having issues? Need help?

- 📧 **Email**: [Create an issue](https://github.com/rah-9/Financial.AI.Agent/issues)
- 📖 **Documentation**: Check this README and code comments
- 🐛 **Bug Reports**: Use GitHub Issues
- 💡 **Feature Requests**: Open a discussion

---

**⭐ If you find this project helpful, please consider giving it a star on GitHub!**

*Built with ❤️ for the financial community*
