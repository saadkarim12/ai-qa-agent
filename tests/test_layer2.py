"""Layer 2 tests.

Safety and honesty first: the crawler drives a live system with real
credentials, so the tests that matter most are the ones proving it refuses to
do damage and never presents a guess as a fact.
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from layer1.contracts import Source
from layer2.analyse import in_scope, signature
from layer2.contracts import ElementKind, SafetyVerdict
from layer2.safety import is_blocked


# --- Safety Governor (no browser needed) -----------------------------------

@pytest.mark.parametrize("name,kind", [
    ("Close account permanently", "submit"),
    ("Delete user", "link"),
    ("Send transfer", "submit"),
    ("Pay now", "button"),
    ("Sign out", "link"),
    ("Purge records", "button"),
])
def test_destructive_actions_are_blocked(name, kind):
    blocked, reason = is_blocked(name, "", "", kind)
    assert blocked, name
    assert reason


@pytest.mark.parametrize("name,kind", [
    ("Sign in", "submit"),
    ("Save changes", "submit"),
    ("Download CSV", "link"),
    ("Help", "link"),
    ("Search", "button"),
])
def test_safe_actions_are_allowed(name, kind):
    blocked, _ = is_blocked(name, "", "", kind)
    assert not blocked, name


def test_navigating_to_a_payments_page_is_allowed_but_submitting_is_not():
    """Discovery must be able to open the transfer form without transacting."""
    assert not is_blocked("Transfer", "", "/transfer", "link")[0]
    assert is_blocked("Send transfer", "", "", "submit")[0]


def test_destructive_styling_is_enough_to_block():
    assert is_blocked("Proceed", "btn danger", "", "submit")[0]


def test_explicit_opt_in_permits_a_destructive_action():
    """C-04: off by default, but an operator can accept the risk knowingly."""
    assert is_blocked("Delete user", "", "", "button", allow_destructive=False)[0]
    assert not is_blocked("Delete user", "", "", "button", allow_destructive=True)[0]


# --- scope and signatures ---------------------------------------------------

def test_offsite_links_are_out_of_scope():
    assert in_scope("http://a.test/x", "https://evil.example/y") is None
    assert in_scope("http://a.test/x", "mailto:me@a.test") is None
    assert in_scope("http://a.test/x", "/dashboard") == "/dashboard"


def test_same_structure_different_data_shares_a_signature():
    """Parameterised routes must not explode the frontier."""
    a = {"headings": ["Order"], "forms": [], "buttons": [{"name": "Back"}], "tables": 1}
    b = {"headings": ["Order"], "forms": [], "buttons": [{"name": "Back"}], "tables": 1}
    c = {"headings": ["Basket"], "forms": [], "buttons": [{"name": "Back"}], "tables": 1}
    assert signature(a) == signature(b)
    assert signature(a) != signature(c)


# --- crawl (real browser, real app) ----------------------------------------

def test_crawl_authenticates_and_reaches_protected_pages(crawled):
    amap, _ = crawled
    assert amap.authenticated
    paths = {p.path for p in amap.pages}
    assert {"/", "/dashboard", "/transfer", "/settings"} <= paths


def test_access_denied_is_detected(crawled):
    amap, _ = crawled
    admin = next((p for p in amap.pages if p.path == "/admin"), None)
    assert admin is not None
    assert admin.access_denied
    assert admin.status == 403


def test_required_fields_are_found(crawled):
    amap, _ = crawled
    transfer = next(p for p in amap.pages if p.path == "/transfer")
    required = [f.name for form in transfer.forms for f in form.required_fields]
    assert "Amount" in required


def test_elements_carry_a_locator_chain_in_preference_order(crawled):
    amap, _ = crawled
    login = next(p for p in amap.pages if p.path == "/login")
    field = next(e for e in login.elements if e.kind is ElementKind.INPUT)
    assert len(field.locators) >= 2
    prefs = [l.preference for l in field.locators]
    assert prefs == sorted(prefs)
    assert field.locators[0].strategy == "role_label"


def test_destructive_elements_are_marked_and_never_clicked(crawled):
    amap, _ = crawled
    settings = next(p for p in amap.pages if p.path == "/settings")
    close = next((e for e in settings.elements if "close account" in e.name.lower()), None)
    assert close is not None
    assert close.safety is SafetyVerdict.BLOCK
    assert any("Close account" in b for b in amap.blocked_actions)


def test_journeys_are_reachable_routes(crawled):
    amap, _ = crawled
    assert amap.journeys
    paths = {p.path for p in amap.pages}
    for j in amap.journeys:
        assert len(j.paths) >= 2
        assert set(j.paths) <= paths
        assert 0.0 < j.confidence < 1.0


# --- discovered requirements ------------------------------------------------

def test_everything_discovered_is_typed_as_discovered(crawled):
    """BR-03: observation is never presented as a confirmed requirement."""
    _, reqs = crawled
    assert reqs
    assert all(r.source is Source.DISCOVERED for r in reqs)
    assert all(not r.is_confirmed for r in reqs)


def test_discovered_requirements_are_never_fully_confident(crawled):
    _, reqs = crawled
    assert all(r.confidence < 1.0 for r in reqs)
    assert all(r.ambiguity_flags for r in reqs)
    assert all(any("inferred" in f for f in r.ambiguity_flags) for r in reqs)


def test_access_denial_becomes_a_critical_requirement(crawled):
    _, reqs = crawled
    denial = [r for r in reqs if r.source_ref.endswith("#access")]
    assert denial
    assert denial[0].risk.value == "Critical"


def test_blocked_actions_become_requirements_flagged_for_manual_testing(crawled):
    """What we refused to click still needs testing - by a human, deliberately."""
    _, reqs = crawled
    blocked = [r for r in reqs if r.source_ref.endswith("#blocked")]
    assert blocked
    assert all("Safety Governor" in " ".join(r.ambiguity_flags) for r in blocked)
    assert all("not verified" in r.expected_outcome for r in blocked)


def test_credentials_never_appear_in_the_map(crawled):
    """C-05 / BR-07: secrets must not reach any artefact."""
    amap, reqs = crawled
    blob = amap.model_dump_json() + " ".join(r.model_dump_json() for r in reqs)
    assert "Passw0rd!23" not in blob
    assert "Adm1nPass" not in blob
