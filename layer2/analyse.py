"""Layer 2 - page analysis.

Everything a page can tell us is pulled out in a single in-page evaluation
rather than dozens of Playwright round-trips. The browser already has the DOM;
asking it once for a structured summary is both faster and easier to reason
about than driving locators one at a time.

Two outputs matter downstream:

  * the locator chain per element (HLD 10.3), in preference order, so Layer 4
    can heal a broken selector by walking down it;
  * the page signature, a structural fingerprint used to dedupe parameterised
    routes so /orders/1, /orders/2 ... do not explode the crawl frontier.
"""

import hashlib
import re
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse

from layer2.contracts import Element, ElementKind, Form, Locator, Page, SafetyVerdict
from layer2.safety import is_blocked

# One pass over the DOM. Returns plain JSON - no Playwright handles escape.
EXTRACT_JS = r"""
() => {
  const vis = el => {
    const r = el.getBoundingClientRect();
    const s = getComputedStyle(el);
    return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none';
  };
  const label = el => {
    if (el.getAttribute('aria-label')) return el.getAttribute('aria-label').trim();
    if (el.id) {
      const l = document.querySelector(`label[for="${CSS.escape(el.id)}"]`);
      if (l && l.innerText.trim()) return l.innerText.trim();
    }
    const wrap = el.closest('label');
    if (wrap && wrap.innerText.trim()) return wrap.innerText.trim();
    if (el.placeholder) return el.placeholder.trim();
    if (el.name) return el.name.trim();
    return '';
  };
  const path = el => {
    const parts = [];
    let node = el;
    while (node && node.nodeType === 1 && parts.length < 5) {
      const parent = node.parentElement;
      if (!parent) break;
      const same = [...parent.children].filter(c => c.tagName === node.tagName);
      parts.unshift(node.tagName.toLowerCase() +
        (same.length > 1 ? `:nth-of-type(${same.indexOf(node) + 1})` : ''));
      node = parent;
    }
    return parts.join(' > ');
  };
  const field = el => ({
    tag: el.tagName.toLowerCase(),
    type: (el.type || '').toLowerCase(),
    name: label(el),
    attrName: el.name || '',
    id: el.id || '',
    testId: el.getAttribute('data-testid') || el.getAttribute('data-test') || '',
    required: el.required === true || el.getAttribute('aria-required') === 'true',
    cls: el.className || '',
    options: el.tagName === 'SELECT' ? [...el.options].map(o => o.text.trim()).slice(0, 12) : [],
    structural: path(el)
  });

  const forms = [...document.forms].map(f => ({
    action: f.getAttribute('action') || '',
    method: (f.getAttribute('method') || 'get').toLowerCase(),
    name: f.getAttribute('name') || f.getAttribute('id') || '',
    fields: [...f.querySelectorAll('input,select,textarea')]
      .filter(el => vis(el) && !['hidden', 'submit', 'button'].includes((el.type || '').toLowerCase()))
      .map(field),
    submit: (() => {
      const b = f.querySelector('button[type=submit],button:not([type]),input[type=submit]');
      if (!b) return null;
      const o = field(b);
      o.name = (b.innerText || b.value || '').trim() || o.name;
      return o;
    })()
  }));

  const buttons = [...document.querySelectorAll('button,input[type=button],[role=button]')]
    .filter(vis).map(b => {
      const o = field(b);
      o.name = (b.innerText || b.value || '').trim() || o.name;
      return o;
    });

  const links = [...document.querySelectorAll('a[href]')].filter(vis).map(a => ({
    href: a.getAttribute('href'),
    name: (a.innerText || '').trim(),
    cls: a.className || '',
    testId: a.getAttribute('data-testid') || '',
    structural: path(a)
  }));

  return {
    title: document.title || '',
    headings: [...document.querySelectorAll('h1,h2,h3')].map(h => h.innerText.trim()).filter(Boolean).slice(0, 12),
    text: (document.body ? document.body.innerText : '').slice(0, 4000),
    tables: document.querySelectorAll('table').length,
    forms, buttons, links
  };
}
"""

_DENIED = re.compile(
    r"\b(access denied|do not have permission|not authorised|not authorized|forbidden)\b",
    re.IGNORECASE,
)
_NEEDS_AUTH = re.compile(
    r"\b(please sign in|please log in|sign in to continue|login required|sign in required)\b",
    re.IGNORECASE,
)


def _kind(tag: str, input_type: str) -> ElementKind:
    if tag == "a":
        return ElementKind.LINK
    if tag == "select":
        return ElementKind.SELECT
    if tag == "textarea":
        return ElementKind.TEXTAREA
    if tag == "button" or input_type in ("submit", "button"):
        return ElementKind.SUBMIT if input_type == "submit" else ElementKind.BUTTON
    if input_type == "checkbox":
        return ElementKind.CHECKBOX
    if input_type == "radio":
        return ElementKind.RADIO
    if tag == "input":
        return ElementKind.INPUT
    return ElementKind.OTHER


def _locators(raw: Dict, kind: ElementKind) -> List[Locator]:
    """Preference order: role/label, test-id, css, structural (HLD 10.3)."""
    out: List[Locator] = []
    name = (raw.get("name") or "").strip()
    if name:
        role = {
            ElementKind.LINK: "link", ElementKind.BUTTON: "button",
            ElementKind.SUBMIT: "button",
        }.get(kind)
        if role:
            out.append(Locator(strategy="role_label",
                               value='get_by_role("%s", name="%s")' % (role, name), preference=0))
        else:
            out.append(Locator(strategy="role_label",
                               value='get_by_label("%s")' % name, preference=0))
    if raw.get("testId"):
        out.append(Locator(strategy="test_id",
                           value='[data-testid="%s"]' % raw["testId"], preference=1))
    if raw.get("id"):
        out.append(Locator(strategy="css", value="#%s" % raw["id"], preference=2))
    elif raw.get("attrName"):
        out.append(Locator(strategy="css",
                           value='%s[name="%s"]' % (raw.get("tag", "*"), raw["attrName"]),
                           preference=2))
    if raw.get("structural"):
        out.append(Locator(strategy="structural", value=raw["structural"], preference=3))
    for i, loc in enumerate(sorted(out, key=lambda l: l.preference)):
        loc.preference = i
    return out


def _element(raw: Dict, allow_destructive: bool, href: str = "") -> Element:
    kind = _kind(raw.get("tag", ""), raw.get("type", ""))
    name = (raw.get("name") or "").strip() or raw.get("attrName") or "(unnamed)"
    blocked, reason = is_blocked(name, raw.get("cls", ""), href, kind.value, allow_destructive)
    return Element(
        kind=kind,
        name=name,
        locators=_locators(raw, kind),
        input_type=raw.get("type") or None,
        required=bool(raw.get("required")),
        options=raw.get("options") or [],
        destructive=blocked or bool(reason),
        safety=SafetyVerdict.BLOCK if blocked else SafetyVerdict.ALLOW,
        safety_reason=reason,
    )


def signature(data: Dict) -> str:
    """Structural fingerprint: same shape, same signature, regardless of data."""
    parts = [
        "h:" + "|".join(sorted(h.lower()[:40] for h in data.get("headings", []))),
        "f:" + "|".join(sorted(
            "%s(%s)" % (f.get("action", ""), len(f.get("fields", [])))
            for f in data.get("forms", [])
        )),
        "b:" + "|".join(sorted((b.get("name") or "").lower() for b in data.get("buttons", []))),
        "t:%d" % data.get("tables", 0),
    ]
    return hashlib.sha256("||".join(parts).encode()).hexdigest()[:16]


def in_scope(base: str, href: str) -> Optional[str]:
    """Resolve a link and keep it only if it stays on the target origin."""
    if not href or href.startswith(("mailto:", "tel:", "javascript:", "#")):
        return None
    absolute = urljoin(base, href)
    b, a = urlparse(base), urlparse(absolute)
    if (a.scheme, a.netloc) != (b.scheme, b.netloc):
        return None
    return a.path or "/"


def analyse(url: str, status: int, data: Dict, allow_destructive: bool) -> Page:
    text = data.get("text", "")
    forms: List[Form] = []
    for f in data.get("forms", []):
        forms.append(Form(
            name=f.get("name") or f.get("action") or "form",
            action=f.get("action") or "",
            method=f.get("method") or "get",
            fields=[_element(x, allow_destructive) for x in f.get("fields", [])],
            submit=_element(f["submit"], allow_destructive) if f.get("submit") else None,
        ))

    elements = [e for form in forms for e in form.fields]
    elements += [form.submit for form in forms if form.submit]
    elements += [_element(b, allow_destructive) for b in data.get("buttons", [])]

    links: List[str] = []
    for a in data.get("links", []):
        path = in_scope(url, a.get("href", ""))
        if path and path not in links:
            links.append(path)
        elements.append(_element(
            dict(a, tag="a", type=""), allow_destructive, href=a.get("href", "")
        ))

    # De-duplicate by name+kind; the same nav link appears on every page.
    seen = set()
    unique: List[Element] = []
    for e in elements:
        key = (e.kind.value, e.name.lower())
        if key not in seen:
            seen.add(key)
            unique.append(e)

    return Page(
        url=url,
        path=urlparse(url).path or "/",
        title=data.get("title", ""),
        status=status,
        signature=signature(data),
        requires_auth=status == 401 or bool(_NEEDS_AUTH.search(text)),
        access_denied=status == 403 or bool(_DENIED.search(text)),
        forms=forms,
        links=links,
        elements=unique,
        headings=data.get("headings", []),
        tables=data.get("tables", 0),
        blocked_actions=[
            "%s (%s)" % (e.name, e.safety_reason)
            for e in unique if e.safety is SafetyVerdict.BLOCK
        ],
    )
