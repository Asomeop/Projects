# Adaptive Token Router & Semantic Gateway

This is an asynchronous LLM proxy microservice that dynamically routes queries across model tiers based on token complexity budgets and leverages vector-based semantic caching to bypass API calls for repetitive tasks at zero token cost.

Basic Overview:
- Accepts raw prompts or agent tasks over HTTP (POST /api/v1/route)
- Intercepts requests using a persistent ChromaDB cosine semantic cache (0 tokens, <25ms latency)
- Calculates prompt token overhead locally using `tiktoken` to classify task complexity
- Dynamically dispatches between low-cost workhorse models (Gemini 2.5 Flash) and frontier reasoning models
- Emits enterprise telemetry including input/output token counts, execution latency, and cost savings metrics
- Fully containerized with Docker

Technologies Used:
- Python 3.11
- FastAPI and Uvicorn
- Pydantic v2
- ChromaDB
- Tiktoken
- Google GenAI SDK (Gemini 2.5 Flash / Gemini Pro)
- Docker

Quick Start with Docker:

1. Add your Google Gemini API key to a .env file in this directory:
   GEMINI_API_KEY=your_key_here

2. Build the Docker image:
   docker build -t token-router-gateway:v1 .

3. Run the container:
   docker run -d -p 8000:8000 --env-file .env --name token-router token-router-gateway:v1

4. Test in your browser:
   http://127.0.0.1:8000/docs