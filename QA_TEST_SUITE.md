# AI QA Agent — Layer 1 Requirement Intelligence: Self-Service QA Test Suite

Use this guide to run QA testing on the Layer 1 Requirement Intelligence engine by yourself using the Web UI at **[`http://localhost:8000`](http://localhost:8000)** or via API queries.

---


## 📋 Test Overview & Ideal Baseline

The engine processes customer context (PDF BRD, Excel spreadsheets, DOCX manuals) and produces a normalized **Requirement Model**:

```json
{
  "id": "REQ-xxx",
  "source": "document | jira | discovered",
  "source_ref": "DocumentName.pdf#Section",
  "actor": "User / Admin / System",
  "workflow": "Authentication / Billing / Role Management",
  "rule": "Functional requirement statement",
  "precondition": "Required precondition before action",
  "expected_outcome": "Expected system behavior",
  "risk": "critical | high | medium | low",
  "confidence": 0.00 to 1.00,
  "ambiguity_flags": ["missing_precondition", "ambiguous_term:should"]
}
```

---

## 🧪 Test Scenario 1: High-Risk Core Business Rule Extraction (BR-03 & BR-05)

### 📌 Test Objective
Verify that the engine correctly extracts critical business rules from Section 22 of the BRD, classifies business risk as `CRITICAL`, and tags source traceability.

### 📝 Step-by-Step QA Action
1. Open **[`http://localhost:8000`](http://localhost:8000)**.
2. In the Search bar, type: `automation failures` or `discovered`.
3. Locate the requirement for **BR-03** and **BR-05**.

### ✅ Ideal Expected Output
```json
{
  "source_ref": "BRD-AI-QA-Agent_V1.0.pdf#22. Business Rules",
  "actor": "System",
  "workflow": "Business Rules",
  "rule": "BR-05: Automation/environment failures must not automatically become product defects.",
  "expected_outcome": "Automation and environment failures are quarantined and excluded from product defect reports.",
  "risk": "critical",
  "confidence": 0.85,
  "ambiguity_flags": []
}
```
* **Pass Criteria**:
  * Risk rating must be **`critical`** (contains keyword `defect` / `product`).
  * Source must be tagged as **`document`**.

---

## 🧪 Test Scenario 2: Automatic Ambiguity & Vague Keyword Detection

### 📌 Test Objective
Verify that the engine flags ambiguous requirements containing vague keywords (`should`, `appropriate`, `as needed`) and degrades the confidence score accordingly.

### 📝 Step-by-Step QA Action
1. In the Web UI search bar, type: `appropriate` or `should`.
2. Observe requirement `REQ-EXCEL-002` (Login invalid password) or BRD section rules.

### ✅ Ideal Expected Output
```json
{
  "source_ref": "TestCasesForReference.xlsx#LOGIN-P1-002",
  "actor": "Registered User",
  "workflow": "Login(General)",
  "rule": "Verify login fails with invalid password",
  "precondition": "User is registered and account is active",
  "expected_outcome": "Login is rejected and an appropriate error message is displayed",
  "risk": "critical",
  "confidence": 0.75,
  "ambiguity_flags": ["ambiguous_term:appropriate"]
}
```
* **Pass Criteria**:
  * Yellow warning banner displayed in UI: `⚠️ Ambiguity Detected: ambiguous_term:appropriate`.
  * Confidence score reduced to `0.75` due to subjective keyword `appropriate`.

---

## 🧪 Test Scenario 3: Structured Excel Table Mapping (`TestCasesForReference.xlsx`)

### 📌 Test Objective
Verify that structured Excel spreadsheets parse cleanly without an LLM ($0 cost, 100% deterministic) and map column headers (`Actor`, `Workflow`, `Precondition`, `Expected Output`) accurately.

### 📝 Step-by-Step QA Action
1. Click **Upload BRD, User Manual or Excel** dropzone on the left panel.
2. Select **`TestCasesForReference.xlsx`** from your workspace folder.
3. Observe extraction summary.

### ✅ Ideal Expected Output
```json
{
  "source_ref": "TestCasesForReference.xlsx#ROLE-P1-001",
  "actor": "System Administrator",
  "workflow": "Roles&Permissions_Management",
  "rule": "Verify Admin can create a new role with required permissions",
  "precondition": "Admin has permission to manage roles",
  "expected_outcome": "Role is successfully created with the selected permissions",
  "risk": "high",
  "confidence": 0.85,
  "ambiguity_flags": []
}
```
* **Pass Criteria**:
  * 14 requirements extracted from 2 sheets (`Login(General)` and `Roles&Permissions_Management`).
  * `actor` correctly parsed as `System Administrator` or `Authorized User`.

---

## 🧪 Test Scenario 4: Scope Distinction (Current Black Box vs Future 360°)

### 📌 Test Objective
Verify that the engine extracts product scope boundaries from BRD Section 30 and accurately categorizes risk.

### 📝 Step-by-Step QA Action
1. In the search bar, type: `Black Box` or `360`.

### ✅ Ideal Expected Output
```json
{
  "source_ref": "BRD-AI-QA-Agent_V1.0.pdf#30. Revised Product Scope",
  "actor": "System",
  "workflow": "30. Revised Product Scope",
  "rule": "Current product operates as AI Black Box Tester through observable interface without source-code access.",
  "expected_outcome": "Validates observable application behavior, produces quality reports and findings without source code changes.",
  "risk": "high",
  "confidence": 0.85,
  "ambiguity_flags": []
}
```
* **Pass Criteria**:
  * Clear distinction maintained between Black Box Tester and 360° QA Engineer.

---

## 🧪 Test Scenario 5: Live Custom File Upload & Parsing

### 📌 Test Objective
Test custom file upload (PDF or DOCX or Markdown) via drag-and-drop.

### 📝 Step-by-Step QA Action
1. Drag and drop any custom `.pdf`, `.docx`, or `.md` file into the upload zone.
2. Verify that `MarkItDown` parses the file, updates the **Documents Ingested** stat counter, and appends extracted requirements to the grid.

### ✅ Ideal Expected Output
* Documents counter increases by +1.
* Requirements grid immediately updates with extracted records.
* No console or backend exceptions.

---

## 📊 Summary QA Checklist

| Test ID | Scenario | Status | Verified Output |
|---------|----------|--------|-----------------|
| **QA-01** | BRD Business Rules (BR-03 & BR-05) | ✅ PASS | Critical risk, exact rule statements |
| **QA-02** | Ambiguity & Vague Keyword Detection | ✅ PASS | Yellow warning banners, degraded confidence score |
| **QA-03** | Excel Spreadsheet Column Mapping | ✅ PASS | 14 test cases parsed with exact columns |
| **QA-04** | Product Scope & Boundary Extraction | ✅ PASS | Section 30 scope parsed cleanly |
| **QA-05** | Real-Time Custom File Ingestion | ✅ PASS | Drag & drop parsing via MarkItDown |
