# KSU IT RAG Chatbot - Project Structure

## Overview
This document outlines the clean, well-organized project structure for the KSU IT RAG Chatbot system.

## Directory Structure

```
Enterprise-Ai__Group-2-Semester_End_Project-main/
├── main.py                          # FastAPI application launcher (root entry point)
├── run_crawler.py                   # Web crawler runner script
├── requirements.txt                 # Python dependencies
├── README.md                        # Project documentation
├── REPORT_TEMPLATE.md               # Project report template
├── .gitignore                       # Git ignore rules
│
├── backend/                         # FastAPI Backend Application
│   └── app/
│       ├── __init__.py              # Backend package initialization
│       ├── main.py                  # FastAPI app setup, middleware, root endpoints
│       ├── config.py                # Application configuration (settings)
│       │
│       ├── api/                     # API Routes
│       │   ├── __init__.py          # API package initialization
│       │   └── routes/
│       │       ├── __init__.py      # Routes module initialization
│       │       └── health.py        # Health check endpoints
│       │
│       ├── models/                  # Data Models
│       │   ├── __init__.py          # Models package initialization
│       │   └── schemas.py           # Pydantic schemas (ChatMessage, ChatResponse, etc.)
│       │
│       ├── services/                # Business Logic Services
│       │   └── __init__.py          # Services package initialization
│       │                           # (RAG, embedding, vector DB, LLM services to be added)
│       │
│       └── utils/                   # Utilities
│           ├── __init__.py          # Utils package initialization
│           └── logger.py            # Logging configuration
│
├── data/                            # Data Processing and Storage
│   ├── crawler/                     # Web Scraping
│   │   ├── __init__.py              # Crawler package initialization
│   │   ├── main.py                  # WebCrawler class and main function
│   │   ├── url_config.py            # URL configuration and settings
│   │   └── utils/
│   │       └── __init__.py          # Crawler utilities (reserved)
│   │
│   ├── raw/                         # Raw scraped data (JSONL files)
│   │   └── kennesaw_uits.jsonl      # Crawled data (1,423 pages)
│   │
│   └── processed/                   # Processed data (for embeddings)
│
└── venv/                            # Virtual environment (not in git)
```

## Code Organization Principles

### 1. **Separation of Concerns**
- **Backend**: API routes, services, models, and utilities are clearly separated
- **Data**: Crawler and data storage are isolated from backend logic
- **Entry Points**: Clear separation between API launcher (`main.py`) and crawler runner (`run_crawler.py`)

### 2. **No Code Duplication**
- ✅ Single health check implementation (detailed in `/api/v1/health/detailed`, simple in `/health`)
- ✅ Logger utility used consistently (no print statements in production code)
- ✅ Configuration centralized in `config.py`
- ✅ Models defined once in `schemas.py`

### 3. **Consistent Documentation**
- All `__init__.py` files have descriptive docstrings
- All modules have clear purpose documentation
- TODO comments are organized and specific

### 4. **Clean Imports**
- Relative imports used within packages
- No circular dependencies
- Clear import hierarchy

## Key Files

### Entry Points
- **`main.py`** (root): Launches FastAPI application via uvicorn
- **`run_crawler.py`**: Runs the web crawler to collect data

### Backend Core
- **`backend/app/main.py`**: FastAPI app initialization, middleware, exception handling
- **`backend/app/config.py`**: Centralized configuration management
- **`backend/app/models/schemas.py`**: Pydantic models for API validation

### Data Collection
- **`data/crawler/main.py`**: WebCrawler class with BFS crawling logic
- **`data/crawler/url_config.py`**: URL configuration and crawl settings

## API Endpoints

### Current Endpoints
- `GET /` - Root endpoint with API information
- `GET /health` - Simple health check
- `GET /api/v1/health/detailed` - Detailed health check with component status
- `GET /docs` - Swagger UI documentation
- `GET /redoc` - ReDoc documentation

### Planned Endpoints (TODOs)
- `POST /api/v1/chat` - Chat endpoint for RAG queries
- `GET /api/v1/documents` - Document management endpoints

## Data Flow

1. **Data Collection**: `run_crawler.py` → `data/crawler/main.py` → `data/raw/kennesaw_uits.jsonl`
2. **Data Processing**: (To be implemented) Process JSONL → Chunk → Embed → Store in Pinecone (Cloud)
3. **API Request**: Frontend → `backend/app/main.py` → Routes → Services → Pinecone (Cloud Vector DB) → LLM → Response

## Cloud Vector Database (Pinecone)

**Why Pinecone?**
- **Team Collaboration**: All team members can access the same vector database
- **No Local Setup**: No need to share large vector database files
- **Scalability**: Cloud-based, handles large datasets efficiently
- **Free Tier Available**: Suitable for development and testing

**Configuration:**
- API credentials stored in `.env` file (not committed to git)
- Shared index name: `ksu-it-rag-chatbot`
- All team members use the same index for consistency

## Best Practices Followed

✅ **Modular Design**: Each component in its own module  
✅ **DRY Principle**: No code duplication  
✅ **Clear Naming**: Descriptive file and function names  
✅ **Documentation**: Comprehensive docstrings  
✅ **Error Handling**: Global exception handler with logging  
✅ **Configuration Management**: Centralized settings  
✅ **Type Hints**: Pydantic models for validation  
✅ **Logging**: Proper logging infrastructure  

## Next Steps for Development

1. **Services Layer**: Implement RAG, embedding, and Pinecone vector DB services
2. **Chat Route**: Create `/api/v1/chat` endpoint
3. **Data Processing**: Build pipeline to process JSONL → chunk → embed → store in Pinecone
4. **Frontend**: React interface for chat interaction

## Team Setup

**For Team Members:**
1. Clone repository
2. Set up virtual environment
3. Install dependencies: `pip install -r requirements.txt`
4. Copy `.env.example` to `.env` and add Pinecone credentials
5. All team members will share the same Pinecone index for collaboration

See `SETUP_GUIDE.md` for detailed setup instructions.

## Notes

- All Python files follow PEP 8 style guidelines
- No linter errors detected
- Project is ready for serious development phase
- Structure is presentation-ready and professional

