import os
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Optional
from semrag.ingestion.engine import IngestionEngine

router = APIRouter()

# Dependency injection for IngestionEngine
ingestion_engine: Optional[IngestionEngine] = None

@router.post("/v1/ingest/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Push-to-Ingest: Upload a local file to the remote SEMRAG server.
    """
    if ingestion_engine is None:
        raise HTTPException(status_code=500, detail="Ingestion Engine not initialized")

    try:
        # v5: Ingest directly from the upload stream (in-memory)
        ingestion_engine.ingest_stream(file.file, file.filename)
        return {"status": "success", "filename": file.filename, "message": "File ingested successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")
