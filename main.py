"""
Main Entry Point for KSU IT RAG Chatbot

This is the FastAPI application entry point. Run with:
    uvicorn main:app --reload
Or:
    python main.py
"""

import uvicorn

if __name__ == "__main__":
    # Use import string for reload to work properly
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
