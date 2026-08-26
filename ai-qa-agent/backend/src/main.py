"""AI QA Agent — Main FastAPI Application & Demo Server.

Serves the Layer 1 Requirement Intelligence API and embedded Web UI.
Includes standalone demo execution with pre-loaded sample datasets.
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any
from uuid import uuid4

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from src.common.config.settings import get_settings
from src.document_ingestion.extraction.hybrid_extractor import HybridRequirementExtractor
from src.document_ingestion.parsers.markitdown_parser import MarkItDownParser
from src.document_ingestion.parsers.xlsx_parser import XlsxParser

settings = get_settings()

app = FastAPI(
    title="AI QA Agent — Requirement Intelligence Engine",
    version="1.0.0",
    description="Software Quality as a Service — Layer 1 Demo Platform",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global in-memory storage for local demo execution
DEMO_PROJECTS: dict[str, dict[str, Any]] = {
    "proj-1": {
        "id": "proj-1",
        "name": "AI QA Agent Platform",
        "application_url": "https://qa-agent.digycorp.com",
        "status": "active",
    }
}

DEMO_DOCUMENTS: list[dict[str, Any]] = []
DEMO_REQUIREMENTS: list[dict[str, Any]] = []

extractor = HybridRequirementExtractor()
markitdown_parser = MarkItDownParser()
xlsx_parser = XlsxParser()

# Uploads directory
UPLOAD_DIR = Path(__file__).resolve().parent.parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)


# --- API Models ---
class ProjectCreateRequest(BaseModel):
    name: str
    application_url: Optional[str] = None
    environment_type: str = "staging"


# --- API Endpoints ---
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "AI QA Agent", "layer": 1}


@app.get("/api/projects")
async def get_projects():
    return list(DEMO_PROJECTS.values())


@app.post("/api/projects")
async def create_project(req: ProjectCreateRequest):
    proj_id = f"proj-{uuid4().hex[:6]}"
    proj = {
        "id": proj_id,
        "name": req.name,
        "application_url": req.application_url,
        "environment_type": req.environment_type,
        "status": "active",
    }
    DEMO_PROJECTS[proj_id] = proj
    return proj


@app.post("/api/upload")
async def upload_document(
    file: UploadFile = File(...), project_id: str = Form("proj-1")
):
    """Upload document, execute MarkItDown conversion, run hybrid requirement extraction."""
    file_id = f"doc-{uuid4().hex[:6]}"
    file_path = UPLOAD_DIR / f"{file_id}_{file.filename}"

    # Save uploaded file
    content = await file.read()
    file_path.write_bytes(content)

    doc_info = {
        "id": file_id,
        "project_id": project_id,
        "filename": file.filename,
        "size_bytes": len(content),
        "status": "processing",
        "requirements_count": 0,
        "warnings": [],
    }
    DEMO_DOCUMENTS.append(doc_info)

    # Parse and extract
    try:
        if file.filename.endswith(".xlsx"):
            parse_res = await xlsx_parser.parse(file_path, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        else:
            parse_res = await markitdown_parser.parse(file_path, "application/octet-stream")

        extracted_candidates = await extractor.extract(parse_res.chunks, file.filename)

        # Convert to API Requirement records
        req_records = []
        for c in extracted_candidates:
            req_id = f"REQ-{uuid4().hex[:6].upper()}"
            record = {
                "id": req_id,
                "project_id": project_id,
                "document_id": file_id,
                "source": "document",
                "source_ref": c.source_ref,
                "actor": c.actor,
                "workflow": c.workflow,
                "rule": c.rule,
                "precondition": c.precondition,
                "expected_outcome": c.expected_outcome,
                "risk": c.risk,
                "confidence": c.confidence,
                "ambiguity_flags": c.ambiguity_flags,
                "extraction_method": c.extraction_method,
            }
            DEMO_REQUIREMENTS.append(record)
            req_records.append(record)

        doc_info["status"] = "completed"
        doc_info["requirements_count"] = len(req_records)
        doc_info["warnings"] = [w.message for w in parse_res.warnings]

        return {
            "document": doc_info,
            "extracted_count": len(req_records),
            "requirements": req_records,
        }

    except Exception as e:
        doc_info["status"] = "failed"
        doc_info["warnings"].append(str(e))
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


@app.get("/api/requirements")
async def list_requirements(
    project_id: str = "proj-1",
    source: Optional[str] = None,
    risk: Optional[str] = None,
    query: Optional[str] = None,
):
    """Filter requirements with optional source, risk, and keyword query."""
    result = DEMO_REQUIREMENTS

    if source:
        result = [r for r in result if r.get("source") == source]
    if risk:
        result = [r for r in result if r.get("risk") == risk]
    if query:
        q = query.lower()
        result = [
            r
            for r in result
            if q in (r.get("rule") or "").lower()
            or q in (r.get("workflow") or "").lower()
            or q in (r.get("actor") or "").lower()
        ]

    return result


@app.get("/api/stats")
async def get_stats():
    """Summary metrics for executive dashboard."""
    total = len(DEMO_REQUIREMENTS)
    critical = sum(1 for r in DEMO_REQUIREMENTS if r.get("risk") == "critical")
    high = sum(1 for r in DEMO_REQUIREMENTS if r.get("risk") == "high")
    ambiguous = sum(1 for r in DEMO_REQUIREMENTS if r.get("ambiguity_flags"))
    discovered = sum(1 for r in DEMO_REQUIREMENTS if r.get("source") == "discovered")

    return {
        "total_requirements": total,
        "critical_count": critical,
        "high_count": high,
        "ambiguous_count": ambiguous,
        "discovered_count": discovered,
        "confirmed_count": total - discovered,
        "documents_ingested": len(DEMO_DOCUMENTS),
    }


# Mount Static Frontend
STATIC_DIR = Path(__file__).resolve().parent.parent / "frontend_dist"
if STATIC_DIR.exists():
    app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")
