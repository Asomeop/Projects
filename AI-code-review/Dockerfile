# 1. Base image: lightweight Python runtime
FROM python:3.11-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Optimize layer caching: Copy and install requirements first
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy the application source code
COPY schemas.py reviewer.py main.py ./

# 5. Expose port 8000 for external traffic
EXPOSE 8000

# 6. Start the FastAPI server with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]