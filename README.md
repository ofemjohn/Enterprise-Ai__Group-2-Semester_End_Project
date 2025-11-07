# KSU IT Department RAG Chatbot

KSU IT RAG Chatbot is a full-stack Retrieval-Augmented Generation system for Kennesaw State University's IT Department. It crawls curated KSU resources, embeds them with Hugging Face, and answers questions with citations via FastAPI, React, and a cloud vector database.

## 🎯 Project Purpose

This chatbot helps students in the KSU IT Department (College of Computing and Software Engineering) find answers to questions about IT services, programs, and resources by searching through official department documentation. Each answer includes source links for accountability and trust.

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: React
- **ML/AI**: Hugging Face Transformers
- **Vector Database**: Pinecone (Cloud-based for team collaboration)
- **Web Scraping**: Playwright + Trafilatura
- **Embeddings**: Sentence Transformers (Hugging Face)

## 📁 Project Structure

```
ksu-it-rag-chatbot/
├── main.py                          # FastAPI application entry point
├── run_crawler.py                   # Web crawler runner script
├── requirements.txt                 # Python dependencies
├── README.md                        # This file
│
├── backend/                         # FastAPI Backend
│   └── app/
│       ├── __init__.py
│       ├── main.py                  # FastAPI application setup
│       ├── api/                     # API routes
│       │   └── routes/
│       ├── services/                # Business logic
│       ├── models/                  # Data models
│       └── utils/                   # Utilities
│
├── data/                            # Data processing and storage
│   ├── crawler/                     # Web scraping scripts
│   │   ├── __init__.py
│   │   ├── main.py                  # Crawler implementation
│   │   ├── url_config.py            # URL configuration
│   │   └── utils/
│   ├── raw/                         # Raw scraped data (JSONL files)
│   └── processed/                   # Processed data ready for embedding
│
└── venv/                            # Virtual environment (not in git)
```

## 🔑 Key Features

1. **Separation of Concerns**: Clear separation between backend, frontend, and data
2. **Modular Design**: Each service/component is in its own file
3. **Team-Friendly**: Easy for non-technical members to understand
4. **Scalable**: Easy to add new features
5. **Documentation**: Comprehensive docs for setup and usage

## 🚀 Getting Started

### Prerequisites

- Python 3.9 or higher
- pip package manager

### Installation

1. **Clone the repository** (if not already done)

2. **Create and activate virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Playwright browsers**:
   ```bash
   playwright install firefox
   ```

5. **Set up environment variables**:
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit .env and add your Pinecone API credentials
   # Get your Pinecone API key from: https://www.pinecone.io/
   ```
   
   **Required environment variables:**
   - `PINECONE_API_KEY`: Your Pinecone API key (get from https://www.pinecone.io/)
   - `PINECONE_ENVIRONMENT`: Your Pinecone environment (e.g., `us-east-1-aws`)
   - `PINECONE_INDEX_NAME`: Name for your vector index (default: `ksu-it-rag-chatbot`)
   
   **Optional environment variables:**
   - `LLM_PROVIDER`: Choose `huggingface` or `openai` (default: `huggingface`)
   - `OPENAI_API_KEY`: Required if using OpenAI
   - `HUGGINGFACE_API_KEY`: Required if using Hugging Face models

### Running the Application

#### Run the Web Crawler

```bash
python run_crawler.py
```

This will crawl KSU IT department websites and save results to `data/raw/kennesaw_uits.jsonl`.

#### Run the FastAPI Backend

```bash
# Option 1: Direct Python execution
python main.py

# Option 2: Using uvicorn directly
uvicorn main:app --reload

# Option 3: Using uvicorn with backend path
uvicorn backend.app.main:app --reload
```

The API will be available at `http://localhost:8000`

- API Documentation: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`

## 📝 Key Files

- `main.py` - FastAPI application entry point
- `run_crawler.py` - Web crawler runner script
- `data/crawler/main.py` - Web crawler implementation
- `data/crawler/url_config.py` - URL configuration for crawling
- `backend/app/main.py` - FastAPI application setup
- `backend/app/config.py` - Application configuration
- `backend/app/models/schemas.py` - API data models
- `requirements.txt` - Python dependencies

## 🚦 Project Status

**Current Phase**: ✅ **FULLY OPERATIONAL** - Ready for Presentation

### ✅ Completed Components

- ✅ **Data Collection**: 1,423 pages crawled from KSU IT websites
- ✅ **Data Processing**: 8,592 knowledge chunks created and embedded
- ✅ **Vector Database**: 8,592 vectors stored in Pinecone (cloud)
- ✅ **RAG Pipeline**: Complete retrieval + generation system
- ✅ **LLM Integration**: Mistral-7B-Instruct via Hugging Face
- ✅ **Backend API**: FastAPI with full documentation
- ✅ **Source Citations**: Automatic URL and snippet extraction
- ✅ **Health Monitoring**: Component status checks

### 📊 System Statistics

- **Pages Crawled**: 1,423
- **Knowledge Chunks**: 8,592
- **Vectors in Database**: 8,592
- **Embedding Dimension**: 384
- **LLM Model**: Mistral-7B-Instruct-v0.2
- **Response Time**: ~2-5 seconds per query

### 🎯 Current Capabilities

The system can answer questions about:
- Password resets and account management
- IT department admission requirements
- Course information and curriculum
- Wi-Fi and network setup
- Service desk contacts
- Software downloads
- And more KSU IT topics...

### 🚧 Future Enhancements

- [ ] React frontend interface
- [ ] Multi-turn conversation support
- [ ] Query history tracking
- [ ] User feedback mechanism

## 👥 Team

Enterprise AI - Group 2 - Semester End Project

**Members:**
- John Ofem
- Kamran Hall
- Lhakpa Sherpa
- Namita Velagapudi

## 📚 Additional Documentation

- `REPORT_TEMPLATE.md` - Template for the project report (4,000-4,800 words)
- `PROJECT_STRUCTURE.md` - Detailed project structure and architecture
- `PRESENTATION_READINESS.md` - Guide for presentation preparation
- `AGENTS.md` - Pinecone best practices reference

## 🎬 Quick Start for Demo

1. **Start the API server**:
   ```bash
   python main.py
   ```

2. **Access API documentation**:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

3. **Test a query**:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "How do I reset my KSU password?"}'
   ```

4. **Check system health**:
   ```bash
   curl http://localhost:8000/api/v1/health/detailed
   ```

---
*Last updated: System fully operational with 8,592 vectors ready for queries*
