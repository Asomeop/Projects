Document RAG API

This is a local RAG microservice that parses PDF documents, converts them into vector embeddings, and uses Google Gemini to answer questions based on the uploaded content.

Basic Overview:
- Accepts PDF file uploads over HTTP (POST /upload)
- Splits text and stores vector embeddings locally in ChromaDB
- Queries ChromaDB and generates grounded answers with page citations (POST /query)
- Fully containerized with Docker

Technologies Used:
- Python 3.11
- FastAPI and Uvicorn
- LangChain
- ChromaDB and Hugging Face Embeddings
- Google Gemini 2.5 Flash
- Docker

Quick Start with Docker:

1. Add your Google Gemini API key to a .env file in this directory:
   GOOGLE_API_KEY=your_key_here

2. Build the Docker image:
   docker build -t document-rag-api .

3. Run the container:
   docker run -d -p 8000:8000 --env-file .env --name rag-service document-rag-api

4. Test in your browser:
   http://127.0.0.1:8000/docs
