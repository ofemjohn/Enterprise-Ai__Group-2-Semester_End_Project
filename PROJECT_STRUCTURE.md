# KSU IT Department RAG Chatbot - Project Structure

## Recommended Project Structure

```
ksu-it-rag-chatbot/
├── README.md                          # Main project documentation
├── .gitignore                         # Git ignore file
├── .env.example                       # Environment variables template
│
├── backend/                           # FastAPI Backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI application entry point
│   │   ├── config.py                  # Configuration settings
│   │   ├── models/                    # Data models
│   │   │   ├── __init__.py
│   │   │   ├── schemas.py             # Pydantic models for API
│   │   │   └── database.py            # Database models (if needed)
│   │   ├── services/                  # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── rag_service.py         # Main RAG logic
│   │   │   ├── embedding_service.py   # Hugging Face embeddings
│   │   │   ├── llm_service.py         # LLM generation
│   │   │   └── vector_db_service.py   # Vector database operations
│   │   ├── api/                       # API routes
│   │   │   ├── __init__.py
│   │   │   ├── routes/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── chat.py            # Chat endpoints
│   │   │   │   ├── documents.py       # Document management
│   │   │   │   └── health.py          # Health check
│   │   ├── utils/                     # Utility functions
│   │   │   ├── __init__.py
│   │   │   ├── logger.py              # Logging setup
│   │   │   └── helpers.py             # Helper functions
│   │   └── tests/                     # Backend tests
│   │       ├── __init__.py
│   │       └── test_rag.py
│   ├── requirements.txt               # Python dependencies
│   └── Dockerfile                     # Docker config (optional)
│
├── frontend/                          # React Frontend
│   ├── public/
│   ├── src/
│   │   ├── components/                # React components
│   │   │   ├── Chat/
│   │   │   │   ├── ChatInterface.jsx
│   │   │   │   ├── MessageList.jsx
│   │   │   │   ├── MessageInput.jsx
│   │   │   │   └── SourceLinks.jsx    # Display source URLs
│   │   │   ├── Layout/
│   │   │   │   ├── Header.jsx
│   │   │   │   └── Footer.jsx
│   │   │   └── Common/
│   │   │       ├── Loading.jsx
│   │   │       └── ErrorBoundary.jsx
│   │   ├── services/                  # API services
│   │   │   ├── api.js                 # API client
│   │   │   └── chatService.js         # Chat API calls
│   │   ├── hooks/                     # Custom React hooks
│   │   │   └── useChat.js
│   │   ├── utils/                     # Frontend utilities
│   │   │   └── constants.js
│   │   ├── App.jsx
│   │   ├── index.jsx
│   │   └── index.css
│   ├── package.json
│   └── README.md
│
├── data/                              # Data processing and storage
│   ├── crawler/                       # Web scraping scripts
│   │   ├── __init__.py
│   │   ├── main.py                    # Main crawler (your existing script)
│   │   ├── url_config.py              # List of URLs to scrape
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── text_processor.py      # Text cleaning utilities
│   ├── raw/                           # Raw scraped data (JSONL files)
│   │   └── .gitkeep
│   ├── processed/                     # Processed data ready for embedding
│   │   └── .gitkeep
│   └── README.md                      # Data documentation
│
├── scripts/                           # Utility scripts
│   ├── setup_environment.sh           # Environment setup script
│   ├── process_data.py                # Process JSONL for embedding
│   └── upload_to_vector_db.py         # Upload embeddings to cloud DB
│
├── docs/                              # Documentation
│   ├── SETUP.md                       # Setup instructions
│   ├── API.md                         # API documentation
│   ├── DEPLOYMENT.md                  # Deployment guide
│   └── CONTRIBUTING.md                # Contribution guidelines
│
└── .github/                           # GitHub workflows (optional)
    └── workflows/
        └── ci.yml
```

## Key Features of This Structure

1. **Separation of Concerns**: Clear separation between backend, frontend, and data
2. **Modular Design**: Each service/component is in its own file
3. **Team-Friendly**: Easy for non-technical members to understand
4. **Scalable**: Easy to add new features
5. **Documentation**: Comprehensive docs for setup and usage

