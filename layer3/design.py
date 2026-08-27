"""Layer 3 - deterministic test design.

Turns each Requirement into the set of tests a competent tester would write for
it. No model is involved: the permutations below are mechanical consequences of
what the requirement says.

The design rule that matters most is the one about *not* generating. Where a
requirement is too vague to test, this emits a clarification request naming what
is missing, rather than inventing an expected result. A confidently-worded test
built on a guess is worse than no test, because someone will trust it.
"""

import re
from typing import Dict, List, Optional, Tuple

from layer1.contracts import Requirement, Risk
from layer3.contracts import TestCase, TestCategory, TestDataRequirement, TestStep

# --- wording patterns ------------------------------------------------------

_WORD_NUMBERS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
    "fifteen": 15, "twenty": 20, "thirty": 30, "sixty": 60,
}
_UNITS = (
    "characters", "character", "minutes", "minute", "times", "attempts",
    "days", "day", "items", "item", "seconds", "hours", "hour", "digits",
)
_QUANTITY = re.compile(
    r"\b(?:at\s+least\s+|at\s+most\s+|more\s+than\s+|less\s+than\s+|up\s+to\s+|older\s+than\s+)?"
    r"(?P<n>\d{1,4}|" + "|".join(_WORD_NUMBERS) + r")\s+"
    r"(?P<unit>" + "|".join(_UNITS) + r")\b",
    re.IGNORECASE,
)
_LOWER_BOUND = re.compile(r"\b(at\s+least|minimum|no\s+fewer\s+than|more\s+than)\b", re.IGNORECASE)

# Negations we can name. A negation we cannot name is not emitted at all.
_NEGATIONS: List[Tuple[str, str, str]] = [
    (r"\bwithout\s+(?:a\s+|an\s+|the\s+)?", "with", "supplying"),
    (r"\bvalid\b", "invalid", "an invalid"),
    (r"\bcorrect\b", "incorrect", "an incorrect"),
    (r"\bactive\b", "inactive", "an inactive"),
    (r"\bregistered\b", "unregistered", "an unregistered"),
    (r"\bauthorised\b", "unauthorised", "an unauthorised"),
    (r"\bauthorized\b", "unauthorized", "an unauthorized"),
    (r"\bcomplete\b", "incomplete", "an incomplete"),
    (r"\bmatching\b", "non-matching", "a non-matching"),
]

_REQUIRED_FIELD = re.compile(
    r"\b(mandatory|required|must\s+(?:contain|include|be\s+(?:provided|supplied|entered))"
    r"|without\s+(?:a\s+|an\s+|the\s+)?(?P<field>[a-z][a-z \-]{2,30}?)\b)",
    re.IGNORECASE,
)
_PERMISSION = re.compile(
    r"\b(access|admin|administrator|permission|role|restricted|denied|forbidden|privilege|/admin)\b",
    re.IGNORECASE,
)
_ROLE_ACTOR = re.compile(
    r"\b(admin|administrator|manager|standard|registered|guest|supplier|policyholder|customer)\b",
    re.IGNORECASE,
)

# Ambiguity flags severe enough that generating a confident test would be a lie.
_BLOCKING_FLAG_MARKERS = (
    "unspecified behaviour",
    "unspecified criterion",
    "non-committal modality",
    "not yet testable",
    "open-ended list",
    "marked tbd",
    "marked tbc",
    "to be decided",
    "leaves the required combination undefined",
)


def _quantity(text: str) -> Optional[Tuple[int, str, bool]]:
    """Return (n, unit, is_lower_bound) if the text states a threshold."""
    m = _QUANTITY.search(text)
    if not m:
        return None
    raw = m.group("n").lower()
    n = int(raw) if raw.isdigit() else _WORD_NUMBERS.get(raw, 0)
    if n <= 0:
        return None
    window = text[max(0, m.start() - 24):m.end()]
    return n, m.group("unit").lower(), bool(_LOWER_BOUND.search(window))


_ALREADY_NEGATIVE = re.compile(
    r"\b(not|never|cannot|can\s?not|must\s+not|no|without|un\w+|in(?:valid|correct|active))\b",
    re.IGNORECASE,
)


def _negate(text: str) -> Optional[Tuple[str, str]]:
    """Return (negated_text, phrase) when the negation can be named.

    A rule that is already negative ("submits an email that is not registered")
    is left alone: negating it again yields a double negative that reads as
    nonsense and tests nothing.
    """
    if _ALREADY_NEGATIVE.search(text):
        return None
    for pattern, replacement, phrase in _NEGATIONS:
        if re.search(pattern, text, re.IGNORECASE):
            return re.sub(pattern, replacement + " ", text, count=1, flags=re.IGNORECASE), phrase
    return None


def _blocking_flags(req: Requirement) -> List[str]:
    return [
        f for f in req.ambiguity_flags
        if any(marker in f.lower() for marker in _BLOCKING_FLAG_MARKERS)
    ]


def _article_fix(text: str) -> str:
    """Repair a/an agreement after a word substitution ("a incorrect")."""
    def swap(m):
        article, word = m.group(1), m.group(2)
        vowel = word[0].lower() in "aeiou"
        fixed = ("an" if vowel else "a")
        if article[0].isupper():
            fixed = fixed.capitalize()
        return "%s %s" % (fixed, word)

    return re.sub(r"\b([Aa]n?)\s+([A-Za-z]+)", swap, text)


def _sentence(text: str) -> str:
    text = _article_fix(re.sub(r"\s+", " ", (text or "").strip()).rstrip("."))
    return text[0].lower() + text[1:] if text else text


class TestDesigner:
    """Requirement[] -> TestCase[]. Deterministic and offline."""

    def __init__(self, prefix: str = "TC"):
        self.prefix = prefix
        self._n = 0
        self._data: Dict[str, TestDataRequirement] = {}

    # -- public ----------------------------------------------------------

    def design(self, requirements: List[Requirement]) -> Tuple[List[TestCase], List[TestDataRequirement]]:
        self._n = 0
        self._data = {}
        cases: List[TestCase] = []
        seen: Dict[Tuple[str, str, str], TestCase] = {}
        for req in requirements:
            for case in self._for_requirement(req):
                key = (case.category.value, case.workflow.lower(), case.title.lower())
                existing = seen.get(key)
                if existing is not None:
                    # Same test, second source. Keep one, merge traceability.
                    for ref in case.requirement_refs:
                        if ref not in existing.requirement_refs:
                            existing.requirement_refs.append(ref)
                    self._n -= 1
                    continue
                seen[key] = case
                cases.append(case)
        for case in cases:
            for did in case.test_data_ids:
                if did in self._data and case.id not in self._data[did].used_by:
                    self._data[did].used_by.append(case.id)
        return cases, list(self._data.values())

    # -- per requirement --------------------------------------------------

    def _for_requirement(self, req: Requirement) -> List[TestCase]:
        blocking = _blocking_flags(req)
        out: List[TestCase] = []

        if blocking:
            # Too vague to design against. Ask, do not guess.
            out.append(self._clarification(req, blocking))
            return out

        out.append(self._positive(req))
        out.extend(self._boundary(req))
        neg = self._negative(req)
        if neg:
            out.append(neg)
        rf = self._required_field(req)
        if rf:
            out.append(rf)
        perm = self._permission(req)
        if perm:
            out.append(perm)
        pre = self._precondition_unmet(req)
        if pre:
            out.append(pre)
        return out

    # -- builders ---------------------------------------------------------

    def _next_id(self) -> str:
        self._n += 1
        return "%s-%03d" % (self.prefix, self._n)

    def _steps(
        self, req: Requirement, action: str, expected: str, setup: Optional[str] = None
    ) -> List[TestStep]:
        steps: List[TestStep] = []
        n = 0
        pre = setup if setup is not None else req.precondition
        if pre:
            n += 1
            steps.append(TestStep(index=n, action="Set up: %s" % _sentence(pre)))
        if req.actor and req.actor.lower() not in ("user", "guest user", "anyone"):
            n += 1
            steps.append(TestStep(index=n, action="Sign in as %s" % req.actor))
        n += 1
        steps.append(TestStep(index=n, action="Go to %s" % req.workflow))
        n += 1
        steps.append(TestStep(index=n, action=action[0].upper() + action[1:]))
        n += 1
        steps.append(TestStep(index=n, action="Observe the result", expected=expected))
        return steps

    def _case(
        self, req: Requirement, category: TestCategory, title: str,
        action: str, expected: str, setup: Optional[str] = None,
        needs_clarification: bool = False, reasons: Optional[List[str]] = None,
    ) -> TestCase:
        steps = self._steps(req, action, expected, setup)
        return TestCase(
            id=self._next_id(),
            title=title,
            category=category,
            actor=req.actor,
            workflow=req.workflow,
            preconditions=[req.precondition] if req.precondition else [],
            steps=steps,
            expected_result=expected,
            requirement_refs=[req.source_ref],
            risk=req.risk,
            priority="P3",           # replaced by the scorer
            score=0.0,
            test_data_ids=self._data_for(req),
            estimated_seconds=30 + 15 * len(steps),
            needs_clarification=needs_clarification,
            clarification_reasons=reasons or [],
        )

    def _positive(self, req: Requirement) -> TestCase:
        return self._case(
            req, TestCategory.POSITIVE,
            "%s - %s" % (req.workflow, _sentence(req.rule)),
            _sentence(req.rule),
            req.expected_outcome,
        )

    def _boundary(self, req: Requirement) -> List[TestCase]:
        q = _quantity("%s %s" % (req.rule, req.expected_outcome))
        if not q:
            return []
        n, unit, lower = q
        out: List[TestCase] = []
        at = self._case(
            req, TestCategory.BOUNDARY,
            "%s - exactly %d %s (on the limit)" % (req.workflow, n, unit),
            "supply exactly %d %s" % (n, unit),
            req.expected_outcome,
        )
        out.append(at)
        if n > 1:
            out.append(self._case(
                req, TestCategory.BOUNDARY,
                "%s - %d %s (just under the limit)" % (req.workflow, n - 1, unit),
                "supply %d %s" % (n - 1, unit),
                "The threshold is not reached, so the stated outcome does not apply "
                "(limit is %d %s)" % (n, unit),
            ))
        return out

    def _negative(self, req: Requirement) -> Optional[TestCase]:
        neg = _negate(req.rule)
        if not neg:
            return None
        negated, phrase = neg
        return self._case(
            req, TestCategory.NEGATIVE,
            "%s - %s" % (req.workflow, _sentence(negated)),
            _sentence(negated),
            "The action is rejected. The success outcome must NOT occur: %s"
            % req.expected_outcome.rstrip("."),
        )

    def _required_field(self, req: Requirement) -> Optional[TestCase]:
        m = _REQUIRED_FIELD.search("%s %s" % (req.rule, req.expected_outcome))
        if not m:
            return None
        field = (m.groupdict().get("field") or "the mandatory field").strip()
        return self._case(
            req, TestCategory.REQUIRED_FIELD,
            "%s - submit with %s left blank" % (req.workflow, field),
            "submit the form with %s left blank" % field,
            "Submission is blocked and a field-level validation message names %s" % field,
        )

    def _permission(self, req: Requirement) -> Optional[TestCase]:
        blob = "%s %s %s" % (req.rule, req.expected_outcome, req.precondition or "")
        if not _PERMISSION.search(blob) or not _ROLE_ACTOR.search(req.actor):
            return None
        return self._case(
            req, TestCategory.PERMISSION,
            "%s - %s attempted by a role without permission"
            % (req.workflow, _sentence(req.rule)),
            "attempt to %s while signed in as a role without that permission" % _sentence(req.rule),
            "Access is refused and no protected data is shown",
            setup="an account holding a role other than %s" % req.actor,
        )

    def _precondition_unmet(self, req: Requirement) -> Optional[TestCase]:
        if not req.precondition:
            return None
        return self._case(
            req, TestCategory.PRECONDITION,
            "%s - precondition not met: %s" % (req.workflow, _sentence(req.precondition)),
            _sentence(req.rule),
            "The action is refused or unavailable because the precondition is not satisfied",
            setup="NOT %s" % _sentence(req.precondition),
        )

    def _clarification(self, req: Requirement, blocking: List[str]) -> TestCase:
        questions = ["What exactly should happen, in observable terms?"]
        for flag in blocking:
            low = flag.lower()
            if "unspecified behaviour" in low or "unspecified criterion" in low:
                questions.append("Define the term used - what counts as success and failure?")
            elif "non-committal" in low:
                questions.append("Is this mandatory or optional? 'should' is not testable.")
            elif "open-ended" in low:
                questions.append("List the full set - 'etc' cannot be tested.")
            elif "not yet testable" in low:
                questions.append("Supply acceptance criteria for this story.")
            elif "tbd" in low or "tbc" in low or "to be decided" in low:
                questions.append("This is still marked undecided - confirm the intended behaviour.")
        return TestCase(
            id=self._next_id(),
            title="%s - clarification needed before a test can be written" % req.workflow,
            category=TestCategory.CLARIFICATION,
            actor=req.actor,
            workflow=req.workflow,
            preconditions=[],
            steps=[TestStep(index=1, action="Not executable. Resolve the questions below first.")],
            expected_result="Undefined - the requirement does not state an observable outcome.",
            requirement_refs=[req.source_ref],
            risk=req.risk,
            priority="P3",
            score=0.0,
            estimated_seconds=0,
            needs_clarification=True,
            clarification_reasons=list(dict.fromkeys(questions)),
            status="Blocked",
        )

    # -- test data --------------------------------------------------------

    def _data_for(self, req: Requirement) -> List[str]:
        blob = ("%s %s %s %s" % (req.actor, req.workflow, req.rule, req.expected_outcome)).lower()
        ids: List[str] = []

        def add(did: str, name: str, desc: str, fields: List[str], sens: str = "synthetic") -> None:
            if did not in self._data:
                self._data[did] = TestDataRequirement(
                    id=did, name=name, description=desc, fields=fields, sensitivity=sens
                )
            if did not in ids:
                ids.append(did)

        actor_key = re.sub(r"[^a-z0-9]+", "-", req.actor.lower()).strip("-") or "user"
        add("TD-ACCOUNT-%s" % actor_key.upper(),
            "%s account" % req.actor,
            "A usable %s account in the test environment" % req.actor,
            ["email", "password", "role", "status"])

        if any(k in blob for k in ("password", "sign in", "log in", "login", "credential")):
            add("TD-CREDENTIALS", "Credential set",
                "Valid and invalid credential pairs, including a locked account",
                ["valid_email", "valid_password", "wrong_password", "unregistered_email"])
        if any(k in blob for k in ("card", "payment", "billing", "refund", "invoice")):
            add("TD-PAYMENT", "Payment instruments",
                "Test card numbers covering authorised, declined and expired outcomes",
                ["card_number", "expiry", "cvv", "billing_address"], "pii-free")
        if any(k in blob for k in ("basket", "order", "checkout", "transfer", "statement")):
            add("TD-TRANSACTION", "Transaction fixtures",
                "Seeded orders/transactions so history-dependent tests are repeatable",
                ["order_id", "amount", "currency", "created_at"])
        if any(k in blob for k in ("admin", "role", "permission", "privilege")):
            add("TD-ROLES", "Role matrix",
                "One account per role so permission tests can cross-check",
                ["role_name", "permissions", "account_email"])
        return ids
