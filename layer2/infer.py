"""Layer 2 - journey and behaviour inference.

This is where HLD 3.4 pays off. Discovery does not produce a second, parallel
kind of artefact: it produces `Requirement` records - the *same* contract
Layer 1 emits from documents - tagged `source = discovered`. One pipeline
follows, and Layer 3 never needs to know where a requirement came from.

BR-03 is what keeps that honest. Everything here is observed behaviour, not
confirmed intent: a `required` attribute tells us the page blocks empty
submission, not that the business wants it to. So every record carries
`source = discovered`, a confidence below 1.0, and an ambiguity flag saying in
plain words that it was inferred from observation.

Inference is deterministic. Each rule below is a direct reading of something
the crawler actually saw.
"""

from collections import deque
from typing import Dict, List, Optional

from layer1.contracts import Requirement, Risk, Source
from layer2.contracts import ApplicationMap, ElementKind, Journey, Page

_INFERRED_NOTE = (
    "inferred from observed application behaviour, not from a confirmed "
    "requirement - confirm with the customer before treating as intent"
)


def _risk_for(path: str, title: str) -> Risk:
    blob = ("%s %s" % (path, title)).lower()
    if any(k in blob for k in ("admin", "audit", "permission", "role", "login", "sign in",
                               "password", "transfer", "payment", "settings")):
        return Risk.CRITICAL
    if any(k in blob for k in ("statement", "download", "profile", "account", "dashboard")):
        return Risk.HIGH
    return Risk.MEDIUM


def _workflow_for(page: Page) -> str:
    if page.headings:
        return page.headings[0][:60]
    if page.title:
        return page.title.split("|")[0].strip()[:60]
    return page.path.strip("/").replace("/", " ").title() or "Home"


def infer_journeys(amap: ApplicationMap) -> List[Journey]:
    """Shortest reachable path from the entry point to each page that does something."""
    graph: Dict[str, List[str]] = {}
    for t in amap.transitions:
        graph.setdefault(t.from_path, [])
        if t.to_path not in graph[t.from_path]:
            graph[t.from_path].append(t.to_path)

    start = "/" if any(p.path == "/" for p in amap.pages) else (
        amap.pages[0].path if amap.pages else None)
    if start is None:
        return []

    # BFS once; every shortest path falls out of the parent map.
    parent: Dict[str, Optional[str]] = {start: None}
    queue = deque([start])
    while queue:
        node = queue.popleft()
        for nxt in graph.get(node, []):
            if nxt not in parent:
                parent[nxt] = node
                queue.append(nxt)

    def path_to(target: str) -> List[str]:
        out, node = [], target
        while node is not None:
            out.append(node)
            node = parent.get(node)
        return list(reversed(out))

    journeys: List[Journey] = []
    for page in amap.pages:
        interesting = bool(page.forms) or page.access_denied
        if not interesting or page.path not in parent or page.path == start:
            continue
        route = path_to(page.path)
        if len(route) < 2:
            continue
        name = _workflow_for(page)
        if page.access_denied:
            rationale = "reachable route that ends in an access-denied response"
            confidence = 0.85
        else:
            fields = sum(len(f.fields) for f in page.forms)
            rationale = "reachable route ending at a form with %d field(s)" % fields
            confidence = 0.75
        journeys.append(Journey(
            name="%s journey" % name,
            paths=route,
            rationale=rationale,
            confidence=confidence,
        ))
    return sorted(journeys, key=lambda j: (-j.confidence, j.name))


def infer_requirements(amap: ApplicationMap) -> List[Requirement]:
    """Observed behaviour -> Requirement[] with source='discovered' (BR-03)."""
    out: List[Requirement] = []
    actor = "Authenticated User" if amap.authenticated else "Guest User"

    for page in amap.pages:
        workflow = _workflow_for(page)
        risk = _risk_for(page.path, page.title)

        # 1. An access-denied response is the strongest signal a crawl produces.
        if page.access_denied:
            out.append(Requirement(
                actor=actor, workflow=workflow,
                rule="The current role opens %s" % page.path,
                precondition="signed in without the role that page requires",
                expected_outcome="Access is refused (HTTP %d) and no protected content is shown"
                                 % page.status,
                risk=Risk.CRITICAL, source=Source.DISCOVERED,
                source_ref="discovered:%s#access" % page.path,
                confidence=0.88,
                ambiguity_flags=[_INFERRED_NOTE],
            ))
            continue

        # 2. A page that demands sign-in states its own access rule.
        if page.requires_auth:
            out.append(Requirement(
                actor="Guest User", workflow=workflow,
                rule="An unauthenticated visitor opens %s" % page.path,
                precondition="no active session",
                expected_outcome="The visitor is asked to sign in and the page content is withheld",
                risk=Risk.CRITICAL, source=Source.DISCOVERED,
                source_ref="discovered:%s#auth" % page.path,
                confidence=0.85,
                ambiguity_flags=[_INFERRED_NOTE],
            ))

        for form in page.forms:
            submit = form.submit.name if form.submit else "Submit"

            # 3. A required attribute means the form blocks empty submission.
            for field in form.required_fields:
                out.append(Requirement(
                    actor=actor, workflow=workflow,
                    rule="The user submits the %s form with %s left empty"
                         % (form.name, field.name),
                    precondition="the %s form is displayed" % form.name,
                    expected_outcome="Submission is blocked and %s is reported as required"
                                     % field.name,
                    risk=risk, source=Source.DISCOVERED,
                    source_ref="discovered:%s#required:%s" % (page.path, field.name),
                    confidence=0.80,
                    ambiguity_flags=[_INFERRED_NOTE],
                ))

            # 4. A select constrains its own input domain.
            for field in form.fields:
                if field.kind is ElementKind.SELECT and field.options:
                    out.append(Requirement(
                        actor=actor, workflow=workflow,
                        rule="The user opens the %s list on the %s form"
                             % (field.name, form.name),
                        precondition="the %s form is displayed" % form.name,
                        expected_outcome="Only these values are offered: %s"
                                         % ", ".join(field.options[:8]),
                        risk=Risk.MEDIUM, source=Source.DISCOVERED,
                        source_ref="discovered:%s#options:%s" % (page.path, field.name),
                        confidence=0.72,
                        ambiguity_flags=[_INFERRED_NOTE],
                    ))

            # 5. The happy path the form exists to serve.
            if form.fields:
                out.append(Requirement(
                    actor=actor, workflow=workflow,
                    rule="The user completes the %s form and selects '%s'" % (form.name, submit),
                    precondition="the %s form is displayed" % form.name,
                    expected_outcome="The submission is accepted and the outcome is confirmed "
                                     "on screen",
                    risk=risk, source=Source.DISCOVERED,
                    source_ref="discovered:%s#submit:%s" % (page.path, form.name),
                    confidence=0.65,
                    ambiguity_flags=[
                        _INFERRED_NOTE,
                        "the successful outcome was not observed - discovery does not submit forms",
                    ],
                ))

    # 6. Anything the Safety Governor refused is still a requirement someone
    #    should test deliberately, by hand, with the risk understood.
    for blocked in amap.blocked_actions:
        path, _, action = blocked.partition(": ")
        out.append(Requirement(
            actor=actor, workflow=path.strip("/").title() or "Home",
            rule="A user selects '%s' on %s" % (action.split(" (")[0], path),
            precondition="the action is visible to the signed-in user",
            expected_outcome="Behaviour not verified - discovery refused to trigger this action",
            risk=Risk.CRITICAL, source=Source.DISCOVERED,
            source_ref="discovered:%s#blocked" % path,
            confidence=0.50,
            ambiguity_flags=[
                _INFERRED_NOTE,
                "blocked by the Safety Governor as potentially destructive - needs a "
                "deliberate, supervised test",
            ],
        ))

    # Same rule discovered on several pages: keep one, first wins.
    seen = set()
    unique: List[Requirement] = []
    for r in out:
        key = (r.rule.lower(), r.expected_outcome.lower())
        if key not in seen:
            seen.add(key)
            unique.append(r)
    return unique
