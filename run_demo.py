#!/usr/bin/env python3
"""AI QA Agent — Single Command Standalone Demo Launcher (Option A).

Launches the FastAPI backend and embedded Web UI locally on http://localhost:8000,
pre-loading extracted requirements from the workspace BRD and Reference Excel files.
"""

import asyncio
import os
import sys
import webbrowser
from pathlib import Path

# Add backend to PYTHONPATH
root_dir = Path(__file__).resolve().parent
backend_dir = root_dir / "ai-qa-agent" / "backend"
sys.path.insert(0, str(backend_dir))

import uvicorn
from src.main import DEMO_DOCUMENTS, DEMO_REQUIREMENTS, app, extractor, markitdown_parser, xlsx_parser


async def preload_sample_data():
    """Pre-load workspace BRD and TestCases Excel into demo memory."""
    brd_pdf = root_dir / "BRD-AI-QA-Agent_V1.0.pdf"
    excel_file = root_dir / "TestCasesForReference.xlsx"

    print("==========================================================")
    print("🚀 AI QA AGENT — LAYER 1 REQUIREMENT INTELLIGENCE DEMO")
    print("==========================================================")

    if excel_file.exists():
        print(f"📦 Pre-loading Excel context: {excel_file.name}")
        excel_res = await xlsx_parser.parse(excel_file, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        reqs = await extractor.extract(excel_res.chunks, excel_file.name)
        for idx, c in enumerate(reqs, start=1):
            DEMO_REQUIREMENTS.append({
                "id": f"REQ-EXCEL-{idx:03d}",
                "project_id": "proj-1",
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
            })
        DEMO_DOCUMENTS.append({
            "id": "doc-excel-01",
            "filename": excel_file.name,
            "status": "completed",
            "requirements_count": len(reqs),
            "warnings": [],
        })

    if brd_pdf.exists():
        print(f"📄 Pre-loading BRD context via MarkItDown: {brd_pdf.name}")
        pdf_res = await markitdown_parser.parse(brd_pdf, "application/pdf")
        reqs = await extractor.extract(pdf_res.chunks, brd_pdf.name)
        for idx, c in enumerate(reqs, start=1):
            DEMO_REQUIREMENTS.append({
                "id": f"REQ-BRD-{idx:03d}",
                "project_id": "proj-1",
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
            })
        DEMO_DOCUMENTS.append({
            "id": "doc-brd-01",
            "filename": brd_pdf.name,
            "status": "completed",
            "requirements_count": len(reqs),
            "warnings": [],
        })

    print(f"✅ Demo Data Preloaded: {len(DEMO_REQUIREMENTS)} total requirements in memory")
    print("==========================================================")


import socket
import subprocess

def free_port(port: int = 8000):
    """Ensure port is available by terminating lingering python server processes if needed."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        if s.connect_ex(("localhost", port)) == 0:
            print(f"⚠️ Port {port} in use. Clearing lingering demo server process...")
            try:
                out = subprocess.check_output(["lsof", "-t", f"-i:{port}"]).decode().strip()
                for pid in out.splitlines():
                    if pid.isdigit():
                        subprocess.run(["kill", "-9", pid], check=False)
            except Exception:
                pass

def main():
    free_port(8000)
    # Preload data synchronously before server start
    asyncio.run(preload_sample_data())

    # Open browser automatically
    print("\n🌐 Opening Web UI at http://localhost:8000 ...")
    webbrowser.open("http://localhost:8000")

    # Start FastAPI server
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")


if __name__ == "__main__":
    main()

