Software Projects Repository

My name is Bryan Miller. Welcome to my software projects repository. This space contains backend applications, AI services, and software engineering projects I am actively building.

Projects:
document-rag-api
  A Retrieval-Augmented Generation (RAG) REST API microservice built with Python, FastAPI, LangChain, ChromaDB, Google Gemini, and Docker. 
  It lets users upload PDF files and ask questions to get grounded answers with page-level citations.

AI-code-review
An automated code quality and security analysis microservice built with Python, FastAPI, Pydantic v2, Google Gemini, and Docker.
It analyzes submitted source code snippets over HTTP for bugs and security vulnerabilities, returning structured JSON feedback with latency metrics.

token-router-gateway
An asynchronous model-routing and context-optimization microservice built with Python, FastAPI, ChromaDB, Tiktoken, Google Gemini, and Docker.
It uses a persistent vector-based semantic cache to intercept repeated queries at zero token cost (<25ms) and dynamically dispatches tasks between lightweight and reasoning model tiers based on token complexity budgets.