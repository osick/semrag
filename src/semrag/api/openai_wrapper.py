import os
import json
import time
from typing import List, Dict, Any, Optional, Union
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv

from semrag.orchestration.graph import SEMRAGGraph
from semrag.api import ingestion, dashboard
from semrag.factory import create_semrag_stack
from semrag.mcp import server_fastmcp

# Load environment variables from .env
load_dotenv()

# Dependency injection for the SEMRAGGraph and Engines
graph: Optional[SEMRAGGraph] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan handler to initialize dependencies on startup.
    """
    global graph
    
    # 1. Initialize the stack using factory
    llm_model = os.getenv("LLM_MODEL", "ollama/llama3")
    embed_model = os.getenv("EMBED_MODEL", "ollama/nomic-embed-text")
    graph_db_type = os.getenv("GRAPH_DB_TYPE", "falkordb")
    
    try:
        ingestion_engine, graph_orchestrator = create_semrag_stack(
            llm_model=llm_model,
            embed_model=embed_model,
            graph_db_type=graph_db_type
        )
        
        # 2. Inject dependencies into API modules
        graph = graph_orchestrator
        ingestion.ingestion_engine = ingestion_engine
        dashboard.graph_store = graph_orchestrator._graph_store
        
        # 3. Inject dependencies into MCP module
        server_fastmcp.graph_orchestrator = graph_orchestrator
        server_fastmcp.ingestion_engine = ingestion_engine
        
        print(f"SEMRAG v5 initialized with model: {llm_model}")
    except Exception as e:
        print(f"CRITICAL: Failed to initialize SEMRAG stack: {e}")
        print("The API will start but retrieval/ingestion will fail until databases are reachable.")
    
    yield
    # Cleanup logic (if any) goes here

app = FastAPI(title="SEMRAG v5 Unified API", lifespan=lifespan)

# Mount Routers
app.include_router(ingestion.router, tags=["ingestion"])
app.include_router(dashboard.router, tags=["dashboard"])

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    stream: bool = False

def get_graph():
    global graph
    if graph is None:
        raise HTTPException(status_code=500, detail="SEMRAG Graph not initialized")
    return graph

@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    """
    OpenAI-compatible chat completion endpoint.
    """
    query = request.messages[-1].content
    semrag_graph = get_graph()
    
    if request.stream:
        async def stream_response():
            result = semrag_graph.run(query)
            chunk = {
                "id": f"chatcmpl-{int(time.time())}",
                "object": "chat.completion.chunk",
                "created": int(time.time()),
                "model": request.model,
                "choices": [{
                    "index": 0,
                    "delta": {"content": result["answer"]},
                    "finish_reason": "stop"
                }]
            }
            yield f"data: {json.dumps(chunk)}\n\n"
            yield "data: [DONE]\n\n"
        
        return StreamingResponse(stream_response(), media_type="text/event-stream")
    
    else:
        result = semrag_graph.run(query)
        return {
            "id": f"chatcmpl-{int(time.time())}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": request.model,
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": result["answer"]
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0
            }
        }

@app.get("/v1/models")
async def list_models():
    """
    OpenAI-compatible models endpoint.
    """
    return {
        "object": "list",
        "data": [
            {"id": "semrag-v5", "object": "model", "created": int(time.time()), "owned_by": "semrag"}
        ]
    }
