"""Layer 1 - deterministic requirement extraction.

Rules first, AI second (ADR-006, ADR-012). Everything in this module is
zero-cost, offline and reproducible: the same document always yields the same
Requirement[]. That matters for three reasons -

  1. Cost. Most QA documents are structured. Paying an LLM to read a
     spreadsheet row is waste (HLD 17.4).
  2. Defensibility. We can tell a customer exactly why a requirement was
     extracted and why it was scored High.
  3. Availability. The demo runs with no API key and no network.

The engine handles four shapes, in priority order:
  A. Labelled fields      - Jira issues, spreadsheet rows ("Actor: ...")
  B. Gherkin              - Given / When / Then
  C. User story + ACs     - "As a X, I want Y" plus acceptance-criteria bullets
  D. Imperative sentences - "The system must ..." / "Users cannot ..."

Anything it cannot crack is reported as an unresolved block so the LLM path
(or a human) can pick it up. Silence is never an option (HLD 4.1).
"""

import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from layer1.contracts import Requirement, Risk, Source
from layer1.parsers import Block

# Story/requirement identifiers, mirrored from parsers so refs strip cleanly.
_ID = r"(?:US|STORY|REQ|AC|PROJ|TC)[-_ ]?\d+"

# --- label vocabulary ------------------------------------------------------

_LABELS: Dict[str, Tuple[str, ...]] = {
    "actor": ("actor", "role", "user", "persona", "as a", "as an", "user type"),
    "workflow": ("workflow", "feature", "epic", "component", "module", "area", "journey"),
    "rule": ("rule", "requirement", "summary", "title", "description", "scenario",
             "test case", "objective", "business rule"),
    "precondition": ("precondition", "pre-condition", "pre condition", "given",
                     "prerequisite", "setup", "context"),
    "expected_outcome": ("expected outcome", "expected result", "expected", "then",
                         "outcome", "acceptance criteria", "result", "acceptance criterion"),
    "risk": ("risk", "priority", "severity", "importance"),
}

# Columns that identify or annotate a row but are not requirement content.
# Checked before the alias map, because "Test Case ID" would otherwise match
# the "test case" alias and become the rule.
_IGNORE_LABELS = (
    "test case id", "testcase id", "case id", "id", "key", "ticket", "issue",
    "status", "pass/fail", "result", "actual output", "actual result",
    "step", "steps", "step(s)", "test data", "notes", "comments", "owner",
    "created", "updated", "release", "sprint", "labels",
)

_LABEL_LINE = re.compile(r"^\s*[\-\*•]?\s*\**\s*([A-Za-z][A-Za-z /_-]{2,30}?)\s*\**\s*[:–-]\s+(.*\S)\s*$")

# --- story / gherkin patterns ---------------------------------------------

_STORY = re.compile(
    r"as\s+an?\s+(?P<actor>[^,\n]{2,60}?)\s*,?\s*i\s+(?:want|need|should be able)\s+(?:to\s+)?"
    r"(?P<goal>[^\n]{3,200}?)(?:\s*,?\s*so\s+that\s+(?P<benefit>[^\n]{3,200}))?\s*\.?\s*$",
    re.IGNORECASE,
)
_GIVEN = re.compile(r"^\s*[\-\*•]?\s*\**given\**\s+(.+?)\s*$", re.IGNORECASE)
_WHEN = re.compile(r"^\s*[\-\*•]?\s*\**(?:when|and when)\**\s+(.+?)\s*$", re.IGNORECASE)
_THEN = re.compile(r"^\s*[\-\*•]?\s*\**(?:then|and then)\**\s+(.+?)\s*$", re.IGNORECASE)
_INLINE_GHERKIN = re.compile(
    r"\bgiven\s+(?P<given>.+?)\s*,?\s+when\s+(?P<when>.+?)\s*,?\s+then\s+(?P<then>.+)$",
    re.IGNORECASE,
)
_INLINE_WHEN_THEN = re.compile(
    r"^\s*when\s+(?P<when>.+?)\s*,?\s+then\s+(?P<then>.+)$", re.IGNORECASE
)
_AC_HEADER = re.compile(r"acceptance\s+criteri(?:a|on)\s*:?\s*$", re.IGNORECASE)
_BULLET = re.compile(r"^\s*(?:[\-\*•]|\d+[\.\)])\s+(.{3,})$")
_MODAL = re.compile(
    r"\b(?:the\s+)?(?P<subj>system|application|user|customer|admin(?:istrator)?|platform|service|page|form)\b"
    r"[^.\n]{0,40}?\b(?P<modal>must|shall|should|will|cannot|can not|must not|is required to|needs to)\b",
    re.IGNORECASE,
)

# --- risk ------------------------------------------------------------------

_PRIORITY_TO_RISK = {
    "blocker": Risk.CRITICAL, "highest": Risk.CRITICAL, "critical": Risk.CRITICAL,
    "p0": Risk.CRITICAL, "sev1": Risk.CRITICAL, "urgent": Risk.CRITICAL,
    "high": Risk.HIGH, "p1": Risk.HIGH, "major": Risk.HIGH, "sev2": Risk.HIGH,
    "medium": Risk.MEDIUM, "p2": Risk.MEDIUM, "normal": Risk.MEDIUM, "moderate": Risk.MEDIUM,
    "low": Risk.LOW, "p3": Risk.LOW, "minor": Risk.LOW, "trivial": Risk.LOW,
}

_RISK_KEYWORDS: List[Tuple[Risk, Tuple[str, ...]]] = [
    (Risk.CRITICAL, ("payment", "billing", "card", "refund", "password", "authentication",
                     "login", "logout", "session", "permission", "privilege", "admin",
                     "encrypt", "gdpr", "pii", "delete", "purge", "audit", "security",
                     "authoris", "authoriz", "invoice", "checkout", "order")),
    (Risk.HIGH, ("register", "sign up", "signup", "role", "access", "validation",
                 "mandatory", "required", "submit", "upload", "download", "integration",
                 "notification", "email", "api", "data", "report")),
    (Risk.LOW, ("tooltip", "colour", "color", "theme", "font", "spacing", "label",
                "footer", "placeholder", "cosmetic", "wording", "icon")),
]

_SEVERITY_ORDER = {Risk.CRITICAL: 0, Risk.HIGH: 1, Risk.MEDIUM: 2, Risk.LOW: 3}

# --- ambiguity -------------------------------------------------------------

_VAGUE_TERMS = {
    "fast": "unquantified performance term 'fast'",
    "quickly": "unquantified performance term 'quickly'",
    "slow": "unquantified performance term 'slow'",
    "user-friendly": "subjective term 'user-friendly'",
    "user friendly": "subjective term 'user friendly'",
    "intuitive": "subjective term 'intuitive'",
    "appropriate": "unspecified criterion 'appropriate'",
    "appropriately": "unspecified criterion 'appropriately'",
    "as needed": "unspecified criterion 'as needed'",
    "as required": "unspecified criterion 'as required'",
    "etc": "open-ended list 'etc' - the full set is undefined",
    "and so on": "open-ended list 'and so on' - the full set is undefined",
    "tbd": "marked TBD - not yet specified",
    "tbc": "marked TBC - not yet confirmed",
    "to be decided": "marked to be decided - not yet specified",
    "reasonable": "subjective term 'reasonable'",
    "seamless": "subjective term 'seamless'",
    "efficient": "subjective term 'efficient'",
    "several": "unquantified quantity 'several'",
    "various": "unquantified quantity 'various'",
    "some": "unquantified quantity 'some'",
    "many": "unquantified quantity 'many'",
    "properly": "unspecified criterion 'properly'",
    "correctly": "unspecified criterion 'correctly'",
    "handle": "unspecified behaviour 'handle' - what happens is not stated",
    "support": "unspecified behaviour 'support' - what happens is not stated",
    "if possible": "conditional 'if possible' - not a testable commitment",
    "where applicable": "conditional 'where applicable' - scope undefined",
    "may": "optional modality 'may' - not a testable commitment",
}

_WEAK_MODALS = ("should", "may", "could", "might", "ideally", "preferably")


@dataclass
class RuleResult:
    requirements: List[Requirement]
    unresolved: List[Block]
    warnings: List[str]


# --- helpers ---------------------------------------------------------------


def _label_of(raw: str) -> Optional[str]:
    key = raw.strip().lower().rstrip(":").strip()
    if key in _IGNORE_LABELS:
        return None
    for field_name, aliases in _LABELS.items():
        if key in aliases:
            return field_name
    for field_name, aliases in _LABELS.items():
        for alias in aliases:
            if key.startswith(alias) or alias in key.split():
                return field_name
    return None


def _labelled_fields(text: str) -> Dict[str, str]:
    """Pull `Label: value` pairs out of a block (Jira issue, spreadsheet row)."""
    out: Dict[str, str] = {}
    for line in text.splitlines():
        m = _LABEL_LINE.match(line)
        if not m:
            continue
        field_name = _label_of(m.group(1))
        if field_name and field_name not in out:
            out[field_name] = m.group(2).strip()
    return out


def infer_risk(text: str, explicit: Optional[str] = None, context: Optional[str] = None) -> Risk:
    """Deterministic risk scoring.

    Precedence: an explicit priority field always wins; then the statement's own
    wording; only then the surrounding story. Scoring a single acceptance
    criterion off its whole parent story made everything Critical.
    """
    if explicit:
        token = explicit.strip().lower()
        for key, risk in _PRIORITY_TO_RISK.items():
            if key in token:
                return risk
    for candidate in (text, context):
        if not candidate:
            continue
        low = candidate.lower()
        # Score every tier and take the best-evidenced one rather than the
        # first in severity order: "the footer colour on the payment page" is a
        # cosmetic change, not a payments change.
        scores = [
            (sum(1 for k in keywords if k in low), risk)
            for risk, keywords in _RISK_KEYWORDS
        ]
        best = max(scores, key=lambda sr: (sr[0], -_SEVERITY_ORDER[sr[1]]))
        if best[0] > 0:
            return best[1]
    return Risk.MEDIUM


def detect_ambiguity(*parts: Optional[str]) -> List[str]:
    """Flag vague, untestable or non-committal wording. HLD 4.1 Ambiguity Detector."""
    text = " ".join(p for p in parts if p)
    low = f" {text.lower()} "
    flags: List[str] = []
    seen = set()

    for term, reason in _VAGUE_TERMS.items():
        if re.search(rf"(?<![\w-]){re.escape(term)}(?![\w-])", low) and reason not in seen:
            flags.append(reason)
            seen.add(reason)

    if re.search(r"\b(must|shall)\b", low) and re.search(r"\b(optional|may|if desired)\b", low):
        flags.append("contradictory modality: states both a mandatory and an optional obligation")
    if not re.search(r"\b(must|shall|will|cannot|is|are|displays?|blocks?|returns?|shows?)\b", low):
        if any(w in low for w in _WEAK_MODALS):
            flags.append("non-committal modality - no mandatory obligation stated")
    if re.search(r"\band\s*/\s*or\b", low):
        flags.append("'and/or' leaves the required combination undefined")
    if len(text.split()) > 60:
        flags.append("statement is long and likely covers multiple rules - split for testability")
    return flags


def _score_confidence(
    actor_explicit: bool,
    workflow_explicit: bool,
    outcome_explicit: bool,
    precondition_found: bool,
    ambiguity_count: int,
) -> float:
    """Confidence is earned from what was actually found, not asserted.

    BR-09: this is extraction confidence, not evidence.
    """
    score = 0.55
    score += 0.15 if actor_explicit else 0.0
    score += 0.10 if workflow_explicit else 0.0
    score += 0.15 if outcome_explicit else 0.0
    score += 0.05 if precondition_found else 0.0
    score -= 0.07 * ambiguity_count
    return round(max(0.10, min(0.99, score)), 2)


def _clean(text: str) -> str:
    text = re.sub(r"\*\*|__|`", "", text).strip()
    text = re.sub(r"\s+", " ", text).rstrip(".;,")
    if text:
        text = text[0].upper() + text[1:]
        if text[-1] not in ".?!":
            text += "."
    return text


def _infer_workflow(text: str, fallback: str) -> Tuple[str, bool]:
    """Guess the workflow from domain keywords when it is not labelled."""
    low = text.lower()
    table = [
        ("Authentication", ("login", "log in", "sign in", "signin", "password", "logout", "mfa", "otp")),
        ("Registration", ("register", "sign up", "signup", "create account", "onboard")),
        ("Checkout", ("checkout", "cart", "basket", "payment", "billing", "order", "invoice")),
        ("User Management", ("role", "permission", "user management", "admin", "privilege")),
        ("Search", ("search", "filter", "sort", "query")),
        ("Reporting", ("report", "export", "dashboard", "analytics", "download")),
        ("Notifications", ("notification", "email", "alert", "sms", "teams")),
        ("Profile", ("profile", "account settings", "preferences")),
        ("Data Management", ("upload", "import", "delete", "archive", "record")),
    ]
    for name, keywords in table:
        if any(k in low for k in keywords):
            return name, True
    return fallback, False


# --- the extractor ---------------------------------------------------------


class RuleExtractor:
    """Deterministic Block[] -> Requirement[]. No network, no model, no cost."""

    def extract(self, blocks: List[Block], source: Source, doc_name: str) -> RuleResult:
        requirements: List[Requirement] = []
        unresolved: List[Block] = []
        warnings: List[str] = []

        for block in blocks:
            try:
                found = self._extract_block(block, source, doc_name)
            except Exception as exc:  # noqa: BLE001 - one bad block must not kill the run
                warnings.append(f"{block.ref}: rule extraction failed ({exc})")
                continue
            if found:
                requirements.extend(found)
            elif len(block.text.split()) >= 6:
                unresolved.append(block)

        return RuleResult(requirements=requirements, unresolved=unresolved, warnings=warnings)

    # -- shape detection ----------------------------------------------------

    def _extract_block(self, block: Block, source: Source, doc_name: str) -> List[Requirement]:
        text = block.text
        fields = _labelled_fields(text)

        actor, actor_explicit = self._actor(text, fields)
        workflow, workflow_explicit = self._workflow(
            text, fields, block.ref, doc_name, hint=getattr(block, "hint", None)
        )
        explicit_priority = fields.get("risk")

        # Shape C: acceptance criteria - each criterion is its own testable rule.
        criteria = self._acceptance_criteria(text)
        if criteria:
            out: List[Requirement] = []
            for i, criterion in enumerate(criteria, start=1):
                req = self._from_statement(
                    statement=criterion,
                    actor=actor,
                    workflow=workflow,
                    actor_explicit=actor_explicit,
                    workflow_explicit=workflow_explicit,
                    source=source,
                    source_ref=f"{block.ref}/AC{i}",
                    explicit_priority=explicit_priority,
                    context=text,
                )
                if req:
                    out.append(req)
            if out:
                return out

        # Shape B: block-level Given/When/Then.
        gherkin = self._gherkin(text)
        if gherkin:
            given, when, then = gherkin
            flags = detect_ambiguity(given, when, then)
            return [
                Requirement(
                    actor=actor,
                    workflow=workflow,
                    rule=_clean(when),
                    precondition=_clean(given) if given else None,
                    expected_outcome=_clean(then),
                    risk=infer_risk(text, explicit_priority),
                    source=source,
                    source_ref=block.ref,
                    confidence=_score_confidence(
                        actor_explicit, workflow_explicit, True, bool(given), len(flags)
                    ),
                    ambiguity_flags=flags,
                )
            ]

        # Shape A': a labelled acceptance-criteria field that is itself a
        # Given/When/Then sentence. Jira exports ACs on a single line, so this
        # must be split rather than stored whole.
        if fields.get("expected_outcome") and self._inline_gherkin(fields["expected_outcome"]):
            req = self._from_statement(
                statement=fields["expected_outcome"],
                actor=actor,
                workflow=workflow,
                actor_explicit=actor_explicit,
                workflow_explicit=workflow_explicit,
                source=source,
                source_ref=block.ref,
                explicit_priority=explicit_priority,
                context=text,
            )
            if req:
                return [req]

        # Shape A: labelled fields (Jira issue, spreadsheet row).
        if fields.get("rule") and fields.get("expected_outcome"):
            flags = detect_ambiguity(fields.get("rule"), fields.get("expected_outcome"))
            return [
                Requirement(
                    actor=actor,
                    workflow=workflow,
                    rule=_clean(fields["rule"]),
                    precondition=_clean(fields["precondition"]) if fields.get("precondition") else None,
                    expected_outcome=_clean(fields["expected_outcome"]),
                    risk=infer_risk(text, explicit_priority),
                    source=source,
                    source_ref=block.ref,
                    confidence=_score_confidence(
                        actor_explicit, workflow_explicit, True,
                        bool(fields.get("precondition")), len(flags),
                    ),
                    ambiguity_flags=flags,
                )
            ]

        # Shape C-minus: a user story with no acceptance criteria at all.
        story = self._story(text)
        if story:
            goal, benefit = story
            flags = detect_ambiguity(goal, benefit)
            outcome_explicit = bool(benefit)
            if outcome_explicit:
                flags.append(
                    "no acceptance criteria - expected outcome derived from the story's "
                    "'so that' benefit, which states value rather than observable behaviour"
                )
            else:
                flags.append("no acceptance criteria or expected outcome stated - not yet testable")
            return [
                Requirement(
                    actor=actor,
                    workflow=workflow,
                    rule=_clean(goal),
                    precondition=_clean(fields["precondition"]) if fields.get("precondition") else None,
                    expected_outcome=_clean(benefit) if benefit else _clean(f"{goal} succeeds"),
                    risk=infer_risk(text, explicit_priority),
                    source=source,
                    source_ref=block.ref,
                    confidence=_score_confidence(
                        actor_explicit, workflow_explicit, outcome_explicit,
                        bool(fields.get("precondition")), len(flags),
                    ),
                    ambiguity_flags=flags,
                )
            ]

        # Shape D: imperative sentences - "the system must ...".
        statements = self._modal_statements(text)
        out = []
        for i, statement in enumerate(statements, start=1):
            ref = block.ref if len(statements) == 1 else f"{block.ref}/R{i}"
            req = self._from_statement(
                statement=statement,
                actor=actor,
                workflow=workflow,
                actor_explicit=actor_explicit,
                workflow_explicit=workflow_explicit,
                source=source,
                source_ref=ref,
                explicit_priority=explicit_priority,
                context=text,
            )
            if req:
                out.append(req)
        return out

    # -- shape parsers ------------------------------------------------------

    def _story(self, text: str) -> Optional[Tuple[str, Optional[str]]]:
        for line in text.splitlines():
            m = _STORY.search(line.strip())
            if m:
                return m.group("goal").strip(), (m.group("benefit") or "").strip() or None
        return None

    def _actor(self, text: str, fields: Dict[str, str]) -> Tuple[str, bool]:
        if fields.get("actor"):
            return _clean(fields["actor"]).rstrip("."), True
        for line in text.splitlines():
            m = _STORY.search(line.strip())
            if m:
                return _clean(m.group("actor")).rstrip("."), True
        for candidate, label in (
            ("admin", "Administrator"), ("customer", "Customer"), ("guest", "Guest User"),
            ("registered user", "Registered User"), ("manager", "Manager"),
        ):
            if candidate in text.lower():
                return label, True
        return "User", False

    def _workflow(
        self, text: str, fields: Dict[str, str], ref: str, doc_name: str,
        hint: Optional[str] = None
    ) -> Tuple[str, bool]:
        if fields.get("workflow"):
            return _clean(fields["workflow"]).rstrip("."), True
        if hint:
            return _clean(hint).rstrip("."), True
        first = next((ln.strip() for ln in text.splitlines() if ln.strip()), "")
        if _LABEL_LINE.match(first):
            # A record-shaped block (spreadsheet row); its first line is data,
            # not a heading.
            return _infer_workflow(text, "General")
        heading = re.sub(r"^#+\s*", "", first)
        heading = re.sub(rf"^{_ID}\s*[:\-—]?\s*", "", heading, flags=re.IGNORECASE).strip()
        heading = re.sub(r"\*\*|__", "", heading).strip()
        if heading and 2 < len(heading) <= 60 and not _STORY.search(heading):
            return heading.rstrip(".:"), True
        return _infer_workflow(text, "General")

    def _acceptance_criteria(self, text: str) -> List[str]:
        lines = text.splitlines()
        start = None
        for i, line in enumerate(lines):
            if _AC_HEADER.search(line):
                start = i + 1
                break
        if start is None:
            return []
        criteria: List[str] = []
        for line in lines[start:]:
            if not line.strip():
                if criteria:
                    continue
                continue
            m = _BULLET.match(line)
            if m:
                criteria.append(m.group(1).strip())
            elif criteria and not _LABEL_LINE.match(line):
                criteria[-1] += " " + line.strip()
            elif _LABEL_LINE.match(line):
                break
        return [c for c in criteria if len(c.split()) >= 3]

    def _gherkin(self, text: str) -> Optional[Tuple[Optional[str], str, str]]:
        given = when = then = None
        for line in text.splitlines():
            if given is None and _GIVEN.match(line):
                given = _GIVEN.match(line).group(1)
            elif when is None and _WHEN.match(line):
                when = _WHEN.match(line).group(1)
            elif then is None and _THEN.match(line):
                then = _THEN.match(line).group(1)
        if when and then:
            return given, when, then
        return None

    def _inline_gherkin(self, statement: str) -> Optional[Tuple[Optional[str], str, str]]:
        """Handle Given/When/Then written as one sentence, which is the norm in ACs."""
        one_line = re.sub(r"\s+", " ", statement).strip()
        m = _INLINE_GHERKIN.search(one_line)
        if m:
            return m.group("given"), m.group("when"), m.group("then")
        m = _INLINE_WHEN_THEN.match(one_line)
        if m:
            return None, m.group("when"), m.group("then")
        return None

    def _modal_statements(self, text: str) -> List[str]:
        out: List[str] = []
        body = re.sub(r"^#+.*$", "", text, flags=re.MULTILINE)
        for raw in re.split(r"(?<=[.!?])\s+|\n", body):
            sentence = raw.strip(" \t-*•")
            if len(sentence.split()) < 4:
                continue
            if _MODAL.search(sentence):
                out.append(sentence)
        return out[:12]

    # -- statement -> Requirement ------------------------------------------

    def _from_statement(
        self,
        statement: str,
        actor: str,
        workflow: str,
        actor_explicit: bool,
        workflow_explicit: bool,
        source: Source,
        source_ref: str,
        explicit_priority: Optional[str],
        context: str,
    ) -> Optional[Requirement]:
        """Turn one criterion/sentence into a Requirement, splitting Gherkin if present."""
        inline = self._inline_gherkin(statement) or self._gherkin(statement)
        precondition = None
        if inline:
            given, when, then = inline
            rule, outcome, outcome_explicit = when, then, True
            precondition = given
        else:
            m = re.search(
                r"^(?P<rule>.+?)\s*(?:,\s*)?\b(?:then|so that|resulting in|and the system\s+)"
                r"(?P<outcome>.+)$",
                statement,
                re.IGNORECASE,
            )
            if m:
                rule, outcome, outcome_explicit = m.group("rule"), m.group("outcome"), True
            else:
                rule, outcome, outcome_explicit = statement, statement, False

        if len(rule.split()) < 3:
            return None

        flags = detect_ambiguity(statement)
        if not outcome_explicit:
            flags.append("expected outcome is not stated separately from the rule")

        return Requirement(
            actor=actor,
            workflow=workflow,
            rule=_clean(rule),
            precondition=_clean(precondition) if precondition else None,
            expected_outcome=_clean(outcome),
            risk=infer_risk(statement, explicit_priority, context=context),
            source=source,
            source_ref=source_ref,
            confidence=_score_confidence(
                actor_explicit, workflow_explicit, outcome_explicit, bool(precondition), len(flags)
            ),
            ambiguity_flags=flags,
        )
