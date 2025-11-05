import os
from functools import lru_cache
import time
from functools import lru_cache 
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from llama_index.core import VectorStoreIndex, Settings
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb

# --- Configuration ---
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://ollama:11434")
CHROMA_HOST_NAME = "chroma" # Use the Docker service name for host
CHROMA_PORT = 8000
LLM_MODEL = os.getenv("LLM_MODEL", "mistral") 
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nomic-embed-text") 
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "unified_rag_store")

# --- LlamaIndex Initialization ---

@lru_cache(maxsize=1) 
def initialize_rag_pipeline():
    """Connects to Chroma and Ollama, and loads the Index."""
    
    # 1. RETRY LOOP FOR CHROMA CONNECTION
    max_retries = 10
    for i in range(max_retries):
        try:
            print(f"Attempting to connect to ChromaDB (Attempt {i+1}/{max_retries})...")
            
            # FIX: Use explicit host and port, which is the most stable syntax
            chroma_client = chromadb.HttpClient(
                host=CHROMA_HOST_NAME,
                port=CHROMA_PORT
            )
            # A simple call to check connectivity; will raise an exception if failed
            chroma_client.list_collections() 
            print("ChromaDB connection successful.")
            
            # If successful, break the retry loop
            break 
        except Exception as e:
            print(f"Chroma connection failed: {e}")
            if i == max_retries - 1:
                # If last attempt failed, raise a detailed error
                raise ConnectionError(f"Failed to connect to ChromaDB after {max_retries} attempts.")
            time.sleep(3) # Wait 3 seconds before next retry
    else:
        # If loop finishes without breaking (i.e., retries failed)
        return None 
    
    # 2. CONTINUED INITIALIZATION (RAG Pipeline)
    try:
        # Get or Create the Collection
        chroma_collection = chroma_client.get_or_create_collection(COLLECTION_NAME)
        # vector_store is now correctly defined here
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection) 
        
        # 3. Initialize Ollama LLM and Embedding Model
        Settings.llm = Ollama(model=LLM_MODEL, base_url=OLLAMA_HOST)
        Settings.embed_model = OllamaEmbedding(
            model_name=EMBEDDING_MODEL,
            base_url=OLLAMA_HOST
        )
        
        # 4. Load the Index and Query Engine
        index = VectorStoreIndex.from_vector_store(
            vector_store=vector_store,
        )
        query_engine = index.as_query_engine(
            similarity_top_k=3,
            streaming=False
        )
        
        return query_engine

    except Exception as e:
        # This catches any errors during the LlamaIndex/Ollama setup
        print(f"Error initializing RAG pipeline (LlamaIndex/Ollama setup): {e}")
        return None

# --- FastAPI Setup and Endpoints ---

app = FastAPI(title="Unified RAG API Gateway", version="1.0")

class QueryRequest(BaseModel):
    query: str
    
class QueryResponse(BaseModel):
    response: str
    
# Global variable for the initialized Query Engine
rag_query_engine = initialize_rag_pipeline()

@app.on_event("startup")
async def startup_event():
    """Ensure the RAG engine is ready before serving requests."""
    if not rag_query_engine:
        raise RuntimeError("RAG pipeline failed to initialize. Check Chroma/Ollama connections.")
    print("Unified RAG API Gateway is ready.")

@app.post("/api/rag/query", response_model=QueryResponse)
async def query_rag_engine(request: QueryRequest):
    """The main endpoint for RAG-augmented query generation."""
    try:
        # The query engine performs the search, prompt augmentation, and LLM call
        response = rag_query_engine.query(request.query)
        
        # You could also include source node metadata here for citations
        return QueryResponse(response=str(response))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG query failed: {e}")

@app.get("/health")
def health_check():
    """Simple health check."""
    return {"status": "ok", "service": "RAG API Gateway"}