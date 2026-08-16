# AI Code Reviewer & Security Analysis API

This is an automated code review microservice that analyzes source code snippets for bugs, security vulnerabilities, and performance issues, returning structured JSON feedback and execution latency metrics using Google Gemini.

Basic Overview:
- Accepts raw code snippets over HTTP (POST /api/v1/review)
- Validates inputs and enforces structured output schemas using Pydantic
- Performs static code analysis and security vulnerability detection via Google Gemini
- Includes health monitoring (GET /health) and latency tracking
- Fully containerized with Docker

Technologies Used:
- Python 3.11
- FastAPI and Uvicorn
- Pydantic v2
- LangChain (`langchain-google-genai`)
- Google Gemini 2.5 Flash
- Docker

Quick Start with Docker:

1. Add your Google Gemini API key to a .env file in this directory:
   GOOGLE_API_KEY=your_key_here

2. Build the Docker image:
   docker build -t ai-code-reviewer:v1 .

3. Run the container:
   docker run -d -p 8000:8000 --env-file .env --name code-reviewer ai-code-reviewer:v1

4. Test in your browser:
   http://127.0.0.1:8000/docs