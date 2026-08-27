"""Layer 1 tests.

The offline rules path is the product's floor, so it is what gets tested:
contract enforcement, each document shape, and reproducibility.
"""

import json
import os
import subprocess
import sys

import pytest
from pydantic import ValidationError

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from layer1.contracts import Requirement, Risk, Source
from layer1.parsers import Block, parse_document, split_story_blocks
from layer1.pipeline import extract_requirements
from layer1.rules import RuleExtractor, detect_ambiguity, infer_risk

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORIES = os.path.join(ROOT, "sample_data", "user_stories.md")
JIRA = os.path.join(ROOT, "sample_data", "jira_sample_issues.json")


def _req(**over):
    base = dict(
        actor="Customer", workflow="Checkout", rule="Billing address is mandatory.",
        expected_outcome="Submission is blocked.", risk=Risk.HIGH,
        source=Source.JIRA, source_ref="PROJ-1", confidence=0.9,
    )
    base.update(over)
    return Requirement(**base)


# --- contract --------------------------------------------------------------

def test_contract_has_exactly_the_hld_fields():
    assert set(_req().model_dump()) == {
        "actor", "workflow", "rule", "precondition", "expected_outcome",
        "risk", "source", "source_ref", "confidence", "ambiguity_flags",
    }


def test_contract_rejects_blank_required_text():
    with pytest.raises(ValidationError):
        _req(rule="   ")


def test_contract_rejects_out_of_range_confidence():
    with pytest.raises(ValidationError):
        _req(confidence=1.4)


def test_contract_rejects_unknown_fields():
    with pytest.raises(ValidationError):
        Requirement(**_req().model_dump(), verified=True)


def test_br03_discovered_is_never_confirmed():
    assert _req(source=Source.JIRA).is_confirmed
    assert _req(source=Source.DOCUMENT).is_confirmed
    assert not _req(source=Source.DISCOVERED).is_confirmed


# --- primitives ------------------------------------------------------------

def test_explicit_priority_beats_keywords():
    # "login" would otherwise score Critical.
    assert infer_risk("user login flow", explicit="Low") is Risk.LOW


def test_statement_wording_beats_surrounding_context():
    assert infer_risk("Change the footer colour", context="payment checkout") is Risk.LOW


def test_ambiguity_detects_vague_and_noncommittal_wording():
    flags = detect_ambiguity("The system should handle errors appropriately, etc.")
    assert any("appropriately" in f for f in flags)
    assert any("etc" in f for f in flags)
    assert len(flags) >= 3


def test_clean_requirement_has_no_ambiguity_flags():
    assert detect_ambiguity(
        "The user submits an incorrect password three times",
        "The account is locked for 15 minutes",
    ) == []


# --- parsing ---------------------------------------------------------------

def test_story_id_becomes_the_source_ref():
    blocks = split_story_blocks("## US-004 Checkout\nAs a Customer, I want to pay.", "stories.md")
    assert blocks[0].ref == "stories.md#US-004"


def test_story_body_stays_with_its_heading():
    text = "## US-001 Login\nAs a User, I want to log in.\n\n## US-002 Reset\nAs a User, I want to reset."
    blocks = split_story_blocks(text, "s.md")
    assert len(blocks) == 2
    assert "log in" in blocks[0].text and blocks[0].ref.endswith("US-001")


# --- shapes ----------------------------------------------------------------

def _extract(text, ref="US-1", source=Source.DOCUMENT, hint=None):
    return RuleExtractor().extract([Block(ref=ref, text=text, hint=hint)], source, "d.md").requirements


def test_each_acceptance_criterion_becomes_its_own_requirement():
    reqs = _extract(
        "## US-001 Login\nAs a User, I want to log in.\n\n"
        "Acceptance Criteria:\n"
        "- When valid credentials are submitted, then the dashboard is shown.\n"
        "- When the password is wrong, then an error is shown.\n"
    )
    assert len(reqs) == 2
    assert [r.source_ref for r in reqs] == ["US-1/AC1", "US-1/AC2"]


def test_inline_gherkin_splits_into_precondition_rule_outcome():
    reqs = _extract(
        "Acceptance Criteria:\n"
        "- Given a locked account, when valid credentials are submitted, "
        "then access is refused with a lockout message.\n"
    )
    assert reqs[0].precondition == "A locked account."
    assert reqs[0].rule == "Valid credentials are submitted."
    assert reqs[0].expected_outcome == "Access is refused with a lockout message."


def test_jira_source_and_ref_are_preserved():
    doc = parse_document(JIRA)
    assert doc.source is Source.JIRA
    result = extract_requirements(JIRA, use_llm=False)
    assert all(r.source is Source.JIRA for r in result.requirements)
    assert any(r.source_ref == "SHOP-1423" for r in result.requirements)


def test_identifier_columns_never_become_the_rule():
    reqs = _extract(
        "Test Case ID: LOGIN-001\n"
        "Test Case Description: Verify login with valid credentials\n"
        "User(s): Registered User\n"
        "Precondition: Account is active\n"
        "Expected Output: The dashboard is displayed",
        hint="Login",
    )
    assert len(reqs) == 1
    assert "LOGIN-001" not in reqs[0].rule
    assert reqs[0].actor == "Registered User"
    assert reqs[0].workflow == "Login"


def test_story_without_acceptance_criteria_is_flagged():
    reqs = _extract("## US-9 Prefs\nAs a User, I want to control emails so that I am not spammed.")
    assert any("acceptance criteria" in f for f in reqs[0].ambiguity_flags)


def test_vague_criterion_scores_low_confidence():
    reqs = _extract("Acceptance Criteria:\n- Search should be fast and user-friendly.\n")
    assert reqs[0].confidence < 0.6
    assert len(reqs[0].ambiguity_flags) >= 3


# --- pipeline --------------------------------------------------------------

def test_offline_run_uses_rules_only():
    result = extract_requirements(STORIES, use_llm=False)
    assert result.extractor == "rules"
    assert set(result.extraction_methods) == {"rules"}
    assert len(result.requirements) >= 10


def test_offline_run_is_deterministic():
    a = extract_requirements(STORIES, use_llm=False)
    b = extract_requirements(STORIES, use_llm=False)
    assert [r.model_dump() for r in a.requirements] == [r.model_dump() for r in b.requirements]


def test_unparseable_blocks_are_reported_not_dropped_silently():
    result = extract_requirements(STORIES, use_llm=False)
    assert any("no recognisable requirement structure" in w for w in result.warnings)


def test_unsupported_format_is_rejected():
    with pytest.raises(ValueError):
        extract_requirements(__file__, use_llm=False)


# --- cli -------------------------------------------------------------------

def test_cli_emits_pure_contract_json(tmp_path):
    out = tmp_path / "reqs.json"
    proc = subprocess.run(
        [sys.executable, "-m", "layer1", STORIES, "--no-llm", "--no-colour", "--json", str(out)],
        cwd=ROOT, capture_output=True, text=True,
    )
    assert proc.returncode == 0, proc.stderr
    records = json.loads(out.read_text())
    assert records
    for rec in records:
        assert set(rec) == {
            "actor", "workflow", "rule", "precondition", "expected_outcome",
            "risk", "source", "source_ref", "confidence", "ambiguity_flags",
        }
        assert rec["risk"] in {"Critical", "High", "Medium", "Low"}
        assert rec["source"] in {"jira", "document", "discovered"}


# --- regressions for defects found by the Layer 1 QA run --------------------

QA = os.path.join(ROOT, "sample_data", "qa")


def test_def01_malformed_jira_export_degrades_instead_of_crashing():
    """A non-object entry in `issues` used to raise AttributeError."""
    result = extract_requirements(os.path.join(QA, "10_malformed.json"), use_llm=False)
    assert result.requirements, "the one well-formed issue should still be extracted"
    assert any("expected an object" in w for w in result.warnings)


def test_def02_docx_bullets_and_tables_are_extracted():
    """Word stores bullets as formatting; the marker must be restored."""
    result = extract_requirements(os.path.join(QA, "15_requirements.docx"), use_llm=False)
    assert len(result.requirements) >= 6
    assert any("/AC" in r.source_ref for r in result.requirements), "AC bullets lost"
    assert any("table" in r.source_ref for r in result.requirements), "table rows lost"


def test_def03_cosmetic_change_outranks_domain_keyword():
    """'footer colour on the payment page' is cosmetic, not a payments change."""
    result = extract_requirements(os.path.join(QA, "12_priority_mapping.json"), use_llm=False)
    by_ref = {r.source_ref: r.risk for r in result.requirements}
    assert by_ref["PRI-1"] is Risk.CRITICAL   # Blocker
    assert by_ref["PRI-2"] is Risk.HIGH       # Major
    assert by_ref["PRI-3"] is Risk.MEDIUM     # Normal
    assert by_ref["PRI-4"] is Risk.LOW        # Trivial
    assert by_ref["PRI-5"] is Risk.LOW        # no priority, cosmetic wording


def test_def04_repeated_criterion_is_flagged():
    result = extract_requirements(os.path.join(QA, "09_duplicates.md"), use_llm=False)
    flagged = [r for r in result.requirements if any("duplicates" in f for f in r.ambiguity_flags)]
    assert len(flagged) == 1
    assert "US-601/AC1" in flagged[0].ambiguity_flags[0]


# --- QA scenario coverage ---------------------------------------------------

def test_prompt_injection_cannot_alter_source_or_confidence():
    """Injected instructions must not change traceability or scoring."""
    result = extract_requirements(os.path.join(QA, "07_prompt_injection.md"), use_llm=False)
    assert result.requirements
    assert all(r.source is Source.DOCUMENT for r in result.requirements)
    assert all(r.confidence <= 0.99 for r in result.requirements)
    assert not any("environment" in r.rule.lower() for r in result.requirements)


def test_document_with_no_requirements_yields_none():
    result = extract_requirements(os.path.join(QA, "05_no_requirements.md"), use_llm=False)
    assert result.requirements == []


def test_empty_document_is_reported():
    result = extract_requirements(os.path.join(QA, "06_empty.md"), use_llm=False)
    assert result.requirements == []
    assert any("no readable blocks" in w for w in result.warnings)


def test_pdf_without_text_layer_warns_about_ocr():
    result = extract_requirements(os.path.join(QA, "16_scanned_no_text.pdf"), use_llm=False)
    assert any("OCR" in w for w in result.warnings)


def test_unicode_content_survives_extraction():
    result = extract_requirements(os.path.join(QA, "08_unicode_multilingual.md"), use_llm=False)
    joined = " ".join(json.dumps(r.model_dump(mode="json"), ensure_ascii=False)
                      for r in result.requirements)
    assert "電子メール通知" in joined      # Japanese
    assert "Réglages enregistrés" in joined  # French accents and guillemets
    assert "£ € ¥ ☑ →" in joined            # currency and arrow symbols


def test_every_ambiguous_requirement_is_flagged():
    result = extract_requirements(os.path.join(QA, "02_ambiguous_requirements.md"), use_llm=False)
    assert result.requirements
    assert all(r.ambiguity_flags for r in result.requirements)
    assert result.stats["avg_confidence"] < 0.65


def test_volume_document_extracts_all_stories():
    result = extract_requirements(os.path.join(QA, "17_large_volume.md"), use_llm=False)
    assert len(result.requirements) == 120  # 60 stories x 2 acceptance criteria
