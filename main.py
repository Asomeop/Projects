import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel, Field
from typing import List
from chromaDB import load_and_split_pdf, embed_and_store_chunks
from query import query_rag


app = FastAPI(
    title="Document RAG Microservice",
    description="A production-ready RAG API for PDF Document QA",
    version="1.0.0"
)

class QueryRequest(BaseModel):
    """Schema for incoming user questions."""
    question: str = Field(
        ..., 
        description="The question to ask about the uploaded document.",
        example="What is the main topic of this paper?"
    )

class Citation(BaseModel):
    """Schema for individual document citations."""
    source: str
    page: int

class QueryResponse(BaseModel):
    """Schema for outgoing API responses."""
    answer: str
    citations: List[Citation]

@app.post("/query", response_model=QueryResponse)
def execute_query(payload: QueryRequest):
    """
    Accepts a question via JSON payload, executes the RAG retrieval chain,
    and returns a structured answer with source citations.
    """
    try:
        # Pass the validated question to our RAG engine
        result = query_rag(payload.question)
        return result
    except Exception as e:
        return {"answer": f"An error occurred: {str(e)}", "citations": []}


@app.post("/upload")
def upload_pdf(file: UploadFile = File(...)):
    """
    Accepts a PDF file upload, splits it into vector chunks, 
    stores them in ChromaDB, and deletes the temporary file.
    """
    # Validate that the uploaded file is actually a PDF
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    # Save the uploaded file temporarily to disk
    temp_file_path = f"temp_{file.filename}"
    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    try:
        # Process the PDF using our chromaDB.py pipeline
        chunks = load_and_split_pdf(temp_file_path)
        embed_and_store_chunks(chunks)
        
        return {
            "status": "success",
            "filename": file.filename,
            "chunks_processed": len(chunks),
            "message": "Document successfully indexed into vector database!"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process PDF: {str(e)}")
    finally:
        # Clean up temporary PDF file from disk
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)