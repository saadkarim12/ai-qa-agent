"""Layer 2 - authentication adapters.

HLD 8.4 lists `IAuthAdapter` as an extensibility seam: form login, SSO, OIDC,
API token, session injection. Only form login is implemented - it is what the
demo target uses - but the seam is what matters, because every enterprise
customer authenticates differently (HLD 10.3) and none of that variation is
allowed to reach the crawler.

Credentials are passed in and used; they are never written to disk, never
logged, and never placed in the Application Map (C-05, BR-07).
"""

from abc import ABC, abstractmethod
from typing import Optional


class IAuthAdapter(ABC):
    name = "none"

    @abstractmethod
    def authenticate(self, page, base_url: str) -> bool:
        """Return True if the session is now authenticated."""


class NoAuth(IAuthAdapter):
    name = "none"

    def authenticate(self, page, base_url: str) -> bool:
        return False


class FormLogin(IAuthAdapter):
    """Fills a username/password form and confirms it left the login page."""

    name = "form"

    def __init__(self, login_path: str, username: str, password: str,
                 user_label: str = "email", pass_label: str = "password",
                 timeout_ms: int = 8000):
        self.login_path = login_path
        self.username = username
        self.password = password
        self.user_label = user_label
        self.pass_label = pass_label
        self.timeout_ms = timeout_ms

    def authenticate(self, page, base_url: str) -> bool:
        page.goto(base_url.rstrip("/") + self.login_path, timeout=self.timeout_ms)
        if not self._fill(page, self.user_label, self.username):
            return False
        if not self._fill(page, self.pass_label, self.password):
            return False
        try:
            page.get_by_role("button", name="Sign in").first.click(timeout=self.timeout_ms)
        except Exception:
            try:
                page.locator("button[type=submit],input[type=submit]").first.click(
                    timeout=self.timeout_ms)
            except Exception:
                return False
        try:
            page.wait_for_load_state("domcontentloaded", timeout=self.timeout_ms)
        except Exception:
            pass
        return self.login_path.rstrip("/") not in (page.url or "")

    def _fill(self, page, label: str, value: str) -> bool:
        for locator in (
            lambda: page.get_by_label(label, exact=False).first,
            lambda: page.locator("#%s" % label).first,
            lambda: page.locator('input[name="%s"]' % label).first,
            lambda: page.locator('input[type="%s"]' % ("password" if "pass" in label else "email")).first,
        ):
            try:
                locator().fill(value, timeout=2500)
                return True
            except Exception:
                continue
        return False
