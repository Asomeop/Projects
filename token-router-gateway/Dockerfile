# Base lightweight Python runtime
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Optimize build caching: copy and install dependencies first
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY schemas.py cache.py router.py main.py ./

# Expose FastAPI default port
EXPOSE 8000

# Start server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]