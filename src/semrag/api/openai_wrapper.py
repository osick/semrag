from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional, Union
import json
import time
from semrag.orchestration.graph import SEMRAGGraph

app = FastAPI(title="SEMRAG OpenAI-Compatible API")

# Dependency injection for the SEMRAGGraph
# In a real app, this would be initialized via a global state or lifespan
graph: Optional[SEMRAGGraph] = None

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    stream: bool = False

def get_graph():
    if graph is None:
        raise HTTPException(status_code=500, detail="SEMRAG Graph not initialized")
    return graph

@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    """
    OpenAI-compatible chat completion endpoint.
    Maps OpenAI request to SEMRAG LangGraph workflow.
    """
    query = request.messages[-1].content
    semrag_graph = get_graph()
    
    if request.stream:
        async def stream_response():
            # For streaming, we provide incremental updates.
            # LangGraph can yield updates, but for now we simulate with a simple yield.
            result = semrag_graph.run(query)
            chunk = {
                "id": "chatcmpl-123",
                "object": "chat.completion.chunk",
                "created": int(time.time()),
                "model": request.model,
                "choices": [{
                    "index": 0,
                    "delta": {"content": result["answer"]},
                    "finish_reason": "stop"
                }]
            }
            yield f"data: {json.dumps(chunk)}

"
            yield "data: [DONE]

"
        
        return StreamingResponse(stream_response(), media_type="text/event-stream")
    
    else:
        # Non-streaming response
        result = semrag_graph.run(query)
        return {
            "id": "chatcmpl-123",
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
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0
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
            {
                "id": "semrag-v2",
                "object": "model",
                "created": int(time.time()),
                "owned_by": "semrag"
            }
        ]
    }
