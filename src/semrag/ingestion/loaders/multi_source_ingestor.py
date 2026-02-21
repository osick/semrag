import fsspec
import os
from typing import List, Dict, Any, Optional
from semrag.ingestion.engine import IngestionEngine

class MultiSourceIngestor:
    """
    Handles multi-source ingestion from local and remote filesystems.
    Uses 'fsspec' for a unified interface (S3, HTTP, GS, Local).
    """
    
    def __init__(self, ingestion_engine: IngestionEngine):
        self._ingestion_engine = ingestion_engine

    def ingest_url(self, url: str, recursive: bool = True) -> None:
        """
        Ingests a URL (local or remote).
        If the URL is a directory, it recursively scans for files.
        """
        fs, path = fsspec.core.url_to_fs(url)
        
        if fs.isdir(path):
            if recursive:
                files = fs.find(path)
                for f in files:
                    if not fs.isdir(f):
                        self._ingest_single_file(fs, f)
            else:
                files = fs.ls(path)
                for f in files:
                    if not fs.isdir(f):
                        self._ingest_single_file(fs, f)
        else:
            self._ingest_single_file(fs, path)

    def _ingest_single_file(self, fs: Any, path: str) -> None:
        """
        Downloads a single file to a temporary location and ingests it.
        """
        # Supported file types (DOCX, XLSX, PPTX, PDF, Markdown)
        ext = os.path.splitext(path)[1].lower()
        if ext in [".pdf", ".docx", ".xlsx", ".pptx", ".md", ".txt"]:
            print(f"Ingesting: {path}")
            
            # Temporary download for 'unstructured' partitioning
            # 'unstructured' often requires a local file path
            local_tmp = f"/tmp/semrag_ingest_{os.path.basename(path)}"
            try:
                fs.get(path, local_tmp)
                self._ingestion_engine.ingest_file(local_tmp)
            except Exception as e:
                print(f"Error ingesting {path}: {e}")
            finally:
                if os.path.exists(local_tmp):
                    os.remove(local_tmp)
        else:
            print(f"Skipping unsupported file type: {path}")
