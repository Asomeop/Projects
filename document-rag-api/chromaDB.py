import os
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

load_dotenv()
CHROMA_PATH = "chroma_db"

def load_and_split_pdf(file_path: str):
    """
    Loads a PDF file and splits its content into manageable chunks.
    """
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    
    # Configuring the text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        length_function=len
    )
    chunks = text_splitter.split_documents(documents)
    return chunks


def embed_and_store_chunks(chunks):
    """
    Converts document chunks to vector embeddings and persists them in ChromaDB.
    """
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # Store chunks in ChromaDB and persist to disk
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_PATH
    )
    
    return vector_store


if __name__ == "__main__":
    sample_pdf = "Test.pdf"
    
    if os.path.exists(sample_pdf):
        print("1. Loading and splitting PDF...")
        processed_chunks = load_and_split_pdf(sample_pdf)
        print(f"   Created {len(processed_chunks)} chunks.")
        
        print("\n2. Embedding chunks and saving to ChromaDB...")
        db = embed_and_store_chunks(processed_chunks)
        print(f"   Successfully stored in local database folder: '{CHROMA_PATH}'")
    else:
        print(f"Please place a test PDF named '{sample_pdf}' in your directory to test.")
