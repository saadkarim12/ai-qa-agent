# AI QA Agent — Software Quality as a Service (SQaaS)
## Development Log & Architecture Summary

---

## 📌 Executive Summary & Product Vision
The **AI QA Agent / AI QA Engineer** is a **Software Quality as a Service (SQaaS)** platform providing on-demand QA engineering for customer applications.

* **Current Baseline (Phases 1–2)**: **AI Black Box Tester** — operating from outside the application using URLs, credentials, optional Jira user stories, and uploaded documentation.
* **Target Vision (Phases 3–5)**: **360° AI QA Engineer** — incorporating White Box code analysis, defect-to-code localization, AI-generated code remediation on dedicated `ai-qa/{finding}` branches, and PR/MR human approval workflows.
* **Core Value Proposition**: *"Give us your application. Get confidence back."*

---

## 🏗️ Technical Architecture & Architectural Planes

The platform follows a **Nine-Layer Reference Architecture** (HLD v1.0, BRD v1.1):

1. **Layer 1 — Requirements Intelligence**: Jira + document ingestion, actor/workflow/rule extraction, ambiguity detection, traceability.
2. **Layer 2 — Black Box Intelligence**: Crawl, auth adapters, page analysis, journey & behavior inference, safety governor.
3. **Layer 3 — Test Intelligence**: Test design, creation, deterministic risk scoring, coverage mapping.
4. **Layer 4 — Execution**: Playwright UI (P1), API/DB/a11y (P3), perf/security (P5) behind `IExecutor` seam.
5. **Layer 5 — Evidence**: Content-addressed (SHA-256) screenshots, traces, logs, HAR, DOM, redaction before egress.
6. **Layer 6 — White Box Intelligence** *(P3)*: Repo connectors, code graph, static analysis, defect-to-code localization.
7. **Layer 7 — Remediation** *(P4)*: Patch sandbox, safety gate, isolated AI branch (`ai-qa/{finding}-{slug}`).
8. **Layer 8 — Validation** *(P4)*: Targeted re-execution, impact-selected regression, static gates.
9. **Layer 9 — Delivery**: Quality score & report, findings + evidence links, release recommendation, webhooks/email/Teams.

---

## 🎯 Strategic Decisions (Option A Implementation)

Based on developer-user alignment for the **Best Live Demo**:

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Demo Option** | **Option A** | Full Interactive Web UI + Hybrid Extractor + 1-Command Local Demo Server |
| **Parsing Engine** | **MarkItDown + Custom Parsers** | Microsoft MarkItDown CLI for PDF/DOCX/HTML/MD conversion, openpyxl for Excel |
| **Requirement Extraction** | **Hybrid (Rules + Claude LLM)** | Table structures parsed via rules ($0 cost, 100% deterministic); narrative prose enriched via Claude 3.5 Sonnet |
| **Memory Engine** | **Document & Requirement Memory** | Historical requirement indexing, keyword search, and change-diffing across scan runs |
| **Demo UX** | **Interactive Dark Mode Web UI** | Visual source badges (🟢 Jira, 🔵 Document, 🟣 Discovered), Risk badges, Ambiguity banners, stats grid |
| **Local Deployment** | **`run_demo.py`** | 1-command launcher (`python3 run_demo.py`) that preloads workspace BRD & Excel into memory and opens `http://localhost:8000` |

---

## 📂 Code Base Structure

```
/Users/saadkarim/Library/CloudStorage/OneDrive-DigyCorp/Documents/QA Agents/
├── BRD-AI-QA-Agent_V1.0.pdf                # Primary BRD specification
├── TestCasesForReference.xlsx              # Reference test case dataset
├── BRD-AI-QA-Agent_V1.0.md                 # Converted Markdown via MarkItDown
├── run_demo.py                             # Single command standalone demo launcher
├── DEVELOPMENT_LOG.md                      # Comprehensive development log (this file)
└── ai-qa-agent/
    ├── backend/
    │   ├── pyproject.toml                  # Python package configuration
    │   ├── src/
    │   │   ├── main.py                     # Main FastAPI application & demo endpoints
    │   │   ├── common/
    │   │   │   ├── config/settings.py      # App settings via pydantic-settings
    │   │   │   ├── db/session.py           # SQLAlchemy async session with RLS
    │   │   │   ├── models/base.py          # Tenant, Project, Document, Requirement, AuditEvent
    │   │   │   └── memory/memory_service.py # Document memory, requirement search & diffing
    │   │   ├── document_ingestion/
    │   │   │   ├── parsers/
    │   │   │   │   ├── base.py             # IDocumentParser interface & ParserRegistry
    │   │   │   │   ├── markitdown_parser.py # Microsoft MarkItDown PDF/DOCX/HTML/MD parser
    │   │   │   │   ├── pdf_parser.py       # pdfplumber table & text fallback
    │   │   │   │   ├── docx_parser.py      # python-docx parser
    │   │   │   │   └── xlsx_parser.py      # openpyxl spreadsheet parser
    │   │   │   └── extraction/
    │   │   │       ├── rule_extractor.py   # Rule-based extractor, risk & ambiguity detector
    │   │   │       └── hybrid_extractor.py # Hybrid extractor (Rules + Claude LLM)
    │   │   └── model_gateway/
    │   │       └── gateway.py              # Model Gateway abstraction (ADR-010)
    │   └── tests/
    │       └── test_layer1_engine.py       # Validation test suite
    └── frontend_dist/
        └── index.html                      # Interactive Dark Mode Web UI
```

---

## ⚡ How to Run the Demo

Execute the single command from the project root:

```bash
python3 run_demo.py
```

This will:
1. Initialize the FastAPI server on `http://localhost:8000`.
2. Pre-load requirements from `BRD-AI-QA-Agent_V1.0.pdf` and `TestCasesForReference.xlsx`.
3. Automatically launch your default browser to `http://localhost:8000`.

---

## 📊 Live Verification Results

Ran `python3 run_demo.py` on the workspace documents:
- **`BRD-AI-QA-Agent_V1.0.pdf`**: Converted to Markdown via `markitdown`, extracting 26 requirement candidates.
- **`TestCasesForReference.xlsx`**: Extracted 14 test cases across `Login(General)` and `Roles&Permissions_Management`.
- **API Endpoints**:
  - `GET /api/stats` → `{"total_requirements": 40, "critical_count": 13, "high_count": 1, "ambiguous_count": 33, "documents_ingested": 2}`
  - `GET /api/requirements` → Returns full structured JSON array of requirements with risk ratings and ambiguity flags.
