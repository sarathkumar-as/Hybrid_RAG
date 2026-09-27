import logging
from contextlib import asynccontextmanager
from typing import Literal

from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool

from . import config
from .service import RAGService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
service = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global service
    try:
        service = await run_in_threadpool(RAGService)
    except Exception:
        logger.exception("RAG dependencies unavailable; /health will report the failure")
    yield
    if service:
        service.close()


app = FastAPI(title="Hybrid RAG API", version="1.0.0", lifespan=lifespan)


def ready():
    if not service:
        raise HTTPException(503, "Service unavailable. Check OPENAI_API_KEY and Neo4j logs.")
    return service


class Question(BaseModel):
    question: str = Field(min_length=3, max_length=2000)
    document_ids: list[str] | None = Field(default=None, max_length=100)


@app.get("/health")
def health():
    if not service:
        raise HTTPException(503, "OpenAI configuration or Neo4j unavailable")
    try:
        service.graph.verify_connectivity()
        return {"status": "ok", "chunks": service.collection.count()}
    except Exception:
        raise HTTPException(503, "Neo4j unavailable")


@app.get("/documents")
async def list_documents():
    worker = ready()
    try:
        return {"documents": await run_in_threadpool(worker.list_documents)}
    except Exception:
        logger.exception("Document listing failed")
        raise HTTPException(502, "Could not list documents. Check backend logs.")


@app.get("/knowledge-graph/summary")
async def graph_summary():
    worker = ready()
    try:
        return await run_in_threadpool(worker.graph_summary)
    except Exception:
        logger.exception("Graph summary failed")
        raise HTTPException(502, "Could not read knowledge graph. Check backend logs.")


@app.get("/knowledge-graph/entities")
async def graph_entities(search: str = Query("", max_length=100), offset: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=100)):
    worker = ready()
    try:
        return await run_in_threadpool(worker.graph_entities, search, offset, limit)
    except Exception:
        logger.exception("Graph entity listing failed")
        raise HTTPException(502, "Could not read graph entities. Check backend logs.")


@app.get("/knowledge-graph/relationships")
async def graph_relationships(search: str = Query("", max_length=100), offset: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=100)):
    worker = ready()
    try:
        return await run_in_threadpool(worker.graph_relationships, search, offset, limit)
    except Exception:
        logger.exception("Graph relationship listing failed")
        raise HTTPException(502, "Could not read graph relationships. Check backend logs.")


@app.get("/knowledge-graph/links")
async def graph_links(kind: Literal["document_chunks", "mentions"], search: str = Query("", max_length=100), offset: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=100)):
    worker = ready()
    try:
        return await run_in_threadpool(worker.graph_links, kind, search, offset, limit)
    except Exception:
        logger.exception("Graph link listing failed")
        raise HTTPException(502, "Could not read graph links. Check backend logs.")


@app.post("/documents")
async def documents(files: list[UploadFile] = File(...)):
    worker = ready()
    if not 1 <= len(files) <= 5:
        raise HTTPException(400, "Upload 1 to 5 PDFs at a time.")
    outputs = []
    for file in files:
        name = (file.filename or "document.pdf").split("/")[-1].split("\\")[-1][:120]
        data = await file.read(config.MAX_UPLOAD_MB * 1024 * 1024 + 1)
        suffix = name.rsplit(".", 1)[-1].lower()
        if suffix not in ("pdf", "docx", "txt", "md") or (suffix == "pdf" and not data.startswith(b"%PDF-")) or (suffix == "docx" and not data.startswith(b"PK")):
            raise HTTPException(400, f"{name}: Supported formats are PDF, DOCX, TXT, and Markdown.")
        if len(data) > config.MAX_UPLOAD_MB * 1024 * 1024:
            raise HTTPException(413, f"{name}: File exceeds {config.MAX_UPLOAD_MB} MB.")
        try:
            outputs.append(await run_in_threadpool(worker.ingest, data, name))
        except ValueError as exc:
            raise HTTPException(422, f"{name}: {exc}")
        except Exception:
            logger.exception("Ingestion failed for %s", name)
            raise HTTPException(502, f"{name}: Ingestion failed. Check backend logs.")
    return {"documents": outputs}


@app.post("/ask")
async def ask(payload: Question):
    worker = ready()
    try:
        return await run_in_threadpool(worker.ask, payload.question.strip(), payload.document_ids)
    except Exception:
        logger.exception("Question processing failed")
        raise HTTPException(502, "Answer generation failed. Check backend logs.")
