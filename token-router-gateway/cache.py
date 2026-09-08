import uuid
from typing import Optional, Tuple
import chromadb
from chromadb.utils import embedding_functions

# Initialize persistent ChromaDB storage in a local folder
chroma_client = chromadb.PersistentClient(path="./chroma_db")

# Default lightweight sentence-transformer embedding function provided by Chroma
default_ef = embedding_functions.DefaultEmbeddingFunction()

# Create or connect to the semantic cache collection using cosine similarity
cache_collection = chroma_client.get_or_create_collection(
    name="semantic_cache",
    embedding_function=default_ef,
    metadata={"hnsw:space": "cosine"}
)

def check_cache(query: str, threshold: float = 0.90) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Checks if a semantically equivalent query exists in the ChromaDB collection.
    Returns (hit_status, cached_response_text, original_matched_prompt).
    """
    results = cache_collection.query(
        query_texts=[query],
        n_results=1
    )

    # Check if any documents exist in the collection
    if not results or not results["documents"] or len(results["documents"][0]) == 0:
        return False, None, None

    # For cosine space: similarity = 1.0 - distance
    cosine_distance = results["distances"][0][0]
    similarity = 1.0 - cosine_distance

    if similarity >= threshold:
        # Cache hit: retrieve stored answer from metadata
        cached_answer = results["metadatas"][0][0].get("response", "")
        matched_prompt = results["documents"][0][0]
        return True, cached_answer, matched_prompt

    return False, None, None

def store_in_cache(query: str, response_text: str, model_used: str) -> None:
    """
    Indexes a new query and its generated response into the semantic cache.
    """
    entry_id = str(uuid.uuid4())
    cache_collection.add(
        ids=[entry_id],
        documents=[query],
        metadatas=[{
            "response": response_text,
            "model_used": model_used
        }]
    )

