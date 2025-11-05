# KSU IT Department RAG Chatbot

KSU IT RAG Chatbot is a full-stack Retrieval-Augmented Generation system for Kennesaw State University's IT Department. It crawls curated KSU resources, embeds them with Hugging Face, and answers questions with citations via FastAPI, React, and a cloud vector database.

## 🎯 Project Purpose

This chatbot helps students in the KSU IT Department (College of Computing and Software Engineering) find answers to questions about IT services, programs, and resources by searching through official department documentation. Each answer includes source links for accountability and trust.

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: React
- **ML/AI**: Hugging Face Transformers
- **Vector Database**: Pinecone (Cloud-based)
- **Web Scraping**: Playwright + Trafilatura

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

**Current Phase**: Foundation Complete, Building Core RAG Pipeline

- ✅ Web crawler functional
- ✅ Project documentation and planning
- ✅ Proper code structure and separation of concerns
- 🚧 RAG pipeline (in progress)
- 🚧 Backend API (basic structure complete)
- 🚧 Frontend interface (planned)
- 📝 Report writing (ready to start)

## 👥 Team

Enterprise AI - Group 2 - Semester End Project

**Members:**
- John Ofem
- Kamran Hall
- Lhakpa Sherpa
- Namita Velagapudi

## 📚 Additional Documentation

- `REPORT_TEMPLATE.md` - Template for the project report (4,000-4,800 words)

---
*Last updated: Repository configured with SSH authentication*
