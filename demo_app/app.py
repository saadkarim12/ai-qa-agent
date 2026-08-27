"""A small web application for Layer 2 to crawl.

Deliberately includes the things a discovery crawler must cope with:
form login and a session, required-field validation, a role-gated page, a
dead end, and a destructive action the Safety Governor has to refuse.

    python3 -m demo_app.app          # serves on 127.0.0.1:8020
"""

import http.server
import socket
import urllib.parse
import uuid
from typing import Dict

USERS = {
    "customer@example.com": {"password": "Passw0rd!23", "role": "customer", "name": "Sam Carter"},
    "admin@example.com": {"password": "Adm1nPass!45", "role": "admin", "name": "Robin Ellis"},
}
SESSIONS: Dict[str, dict] = {}
BALANCES = {"Current": 1840.55, "Savings": 12300.00}

_CSS = """
body{font:15px/1.5 -apple-system,system-ui,sans-serif;margin:0;background:#f6f7f9;color:#1c2128}
header{background:#12203a;color:#fff;padding:14px 22px;display:flex;gap:18px;align-items:center}
header a{color:#cfe0ff;text-decoration:none;font-size:14px}
main{max-width:720px;margin:26px auto;background:#fff;padding:26px;border:1px solid #e2e5ea;border-radius:10px}
h1{margin:0 0 4px;font-size:21px} h2{font-size:16px;margin:22px 0 8px}
label{display:block;margin:12px 0 4px;font-size:13px;color:#4a5261}
input,select{width:100%;padding:9px;border:1px solid #ccd2da;border-radius:7px;font:inherit}
button{margin-top:16px;padding:10px 16px;border:0;border-radius:7px;background:#1b4fd8;color:#fff;font:inherit;cursor:pointer}
button.danger{background:#c62828}
.err{background:#fdecea;border:1px solid #f5c2c0;color:#a3120a;padding:9px 12px;border-radius:7px;margin:12px 0;font-size:14px}
.ok{background:#e8f5e9;border:1px solid #bcdfbf;color:#1b5e20;padding:9px 12px;border-radius:7px;margin:12px 0;font-size:14px}
table{width:100%;border-collapse:collapse;margin-top:10px}
th,td{text-align:left;padding:8px;border-bottom:1px solid #e6e9ee;font-size:14px}
"""


def page(title, body, user=None):
    nav = '<a href="/">Home</a>'
    if user:
        nav += ('<a href="/dashboard">Dashboard</a><a href="/transfer">Transfer</a>'
                '<a href="/statements">Statements</a><a href="/settings">Settings</a>')
        if user["role"] == "admin":
            nav += '<a href="/admin">Admin</a>'
        nav += '<a href="/logout">Sign out</a>'
    else:
        nav += '<a href="/login">Sign in</a>'
    return ("<!doctype html><html><head><meta charset='utf-8'><title>%s</title>"
            "<style>%s</style></head><body><header><b>Northwind Bank</b>%s</header>"
            "<main>%s</main></body></html>" % (title, _CSS, nav, body)).encode()


class App(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *a):
        pass

    # -- helpers ---------------------------------------------------------
    def _user(self):
        cookie = self.headers.get("Cookie") or ""
        for part in cookie.split(";"):
            if part.strip().startswith("sid="):
                return SESSIONS.get(part.strip()[4:])
        return None

    def _send(self, body, code=200, headers=None):
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        for k, v in (headers or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def _redirect(self, to, headers=None):
        self.send_response(302)
        self.send_header("Location", to)
        self.send_header("Content-Length", "0")
        for k, v in (headers or {}).items():
            self.send_header(k, v)
        self.end_headers()

    def _form(self):
        n = int(self.headers.get("Content-Length") or 0)
        return {k: v[0] for k, v in urllib.parse.parse_qs(self.rfile.read(n).decode()).items()}

    # -- routes ----------------------------------------------------------
    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        user = self._user()

        if path == "/":
            return self._send(page("Northwind Bank", (
                "<h1>Northwind Bank</h1><p>Online banking for personal customers.</p>"
                "<h2>Get started</h2><p><a href='/login'>Sign in to your account</a></p>"
                "<p><a href='/help'>Help and FAQs</a></p>"), user))

        if path == "/help":
            return self._send(page("Help", "<h1>Help</h1><p>Call us on 0800 000 000.</p>", user))

        if path == "/login":
            if user:
                return self._redirect("/dashboard")
            return self._send(page("Sign in", (
                "<h1>Sign in</h1><form method='post' action='/login'>"
                "<label for='email'>Email address</label>"
                "<input id='email' name='email' type='email' required>"
                "<label for='password'>Password</label>"
                "<input id='password' name='password' type='password' required>"
                "<button type='submit'>Sign in</button></form>")))

        if path == "/logout":
            return self._redirect("/", {"Set-Cookie": "sid=; Max-Age=0; Path=/"})

        if not user and path in ("/dashboard", "/transfer", "/statements", "/settings", "/admin"):
            return self._send(page("Sign in required",
                                   "<div class='err'>Please sign in to continue.</div>"
                                   "<p><a href='/login'>Sign in</a></p>"), 401)

        if path == "/dashboard":
            rows = "".join("<tr><td>%s</td><td>&pound;%.2f</td></tr>" % (k, v)
                           for k, v in BALANCES.items())
            return self._send(page("Dashboard", (
                "<h1>Dashboard</h1><p>Welcome back, %s.</p>"
                "<table><tr><th>Account</th><th>Balance</th></tr>%s</table>"
                "<p><a href='/transfer'>Make a transfer</a></p>" % (user["name"], rows)), user))

        if path == "/transfer":
            opts = "".join("<option>%s</option>" % k for k in BALANCES)
            return self._send(page("Transfer", (
                "<h1>Transfer funds</h1><form method='post' action='/transfer'>"
                "<label for='from'>From account</label><select id='from' name='from'>%s</select>"
                "<label for='to'>To account</label><select id='to' name='to'>%s</select>"
                "<label for='amount'>Amount</label>"
                "<input id='amount' name='amount' type='number' step='0.01' required>"
                "<label for='reference'>Reference</label><input id='reference' name='reference'>"
                "<button type='submit'>Send transfer</button></form>" % (opts, opts)), user))

        if path == "/statements":
            return self._send(page("Statements", (
                "<h1>Statements</h1><table><tr><th>Date</th><th>Description</th><th>Amount</th></tr>"
                "<tr><td>02 Aug</td><td>Grocery</td><td>&pound;42.10</td></tr>"
                "<tr><td>04 Aug</td><td>Salary</td><td>&pound;2,400.00</td></tr></table>"
                "<p><a href='/statements/download'>Download CSV</a></p>"), user))

        if path == "/statements/download":
            return self._send(page("Download", "<h1>Download</h1><div class='ok'>"
                                   "Your statement is being prepared.</div>", user))

        if path == "/settings":
            return self._send(page("Settings", (
                "<h1>Settings</h1><form method='post' action='/settings'>"
                "<label for='display'>Display name</label>"
                "<input id='display' name='display' value='%s' required>"
                "<button type='submit'>Save changes</button></form>"
                "<h2>Danger zone</h2><form method='post' action='/close-account'>"
                "<button class='danger' type='submit'>Close account permanently</button></form>"
                % user["name"]), user))

        if path == "/admin":
            if user["role"] != "admin":
                return self._send(page("Access denied",
                                       "<div class='err'>You do not have permission to view "
                                       "this page.</div>", user), 403)
            return self._send(page("Admin", "<h1>Administration</h1>"
                                            "<p>Audit log and user management.</p>", user))

        return self._send(page("Not found", "<h1>Page not found</h1>", user), 404)

    def do_POST(self):
        path = urllib.parse.urlparse(self.path).path
        user = self._user()
        form = self._form()

        if path == "/login":
            email, pw = form.get("email", ""), form.get("password", "")
            record = USERS.get(email)
            if not email or not pw:
                return self._send(page("Sign in", "<div class='err'>Email address and password "
                                                  "are both required.</div>"), 400)
            if not record or record["password"] != pw:
                return self._send(page("Sign in", "<div class='err'>Invalid credentials. Please "
                                                  "check your details and try again.</div>"), 401)
            sid = uuid.uuid4().hex
            SESSIONS[sid] = record
            return self._redirect("/dashboard", {"Set-Cookie": "sid=%s; Path=/" % sid})

        if not user:
            return self._send(page("Sign in required", "<div class='err'>Please sign in.</div>"), 401)

        if path == "/transfer":
            amount = form.get("amount", "").strip()
            if not amount:
                return self._send(page("Transfer", "<div class='err'>Amount is required.</div>"
                                                   "<p><a href='/transfer'>Back</a></p>"), 400)
            try:
                value = float(amount)
            except ValueError:
                return self._send(page("Transfer", "<div class='err'>Amount must be a "
                                                   "number.</div>"), 400)
            if value <= 0:
                return self._send(page("Transfer", "<div class='err'>Amount must be greater "
                                                   "than zero.</div>"), 400)
            if value > BALANCES.get(form.get("from", ""), 0):
                return self._send(page("Transfer", "<div class='err'>Insufficient funds for "
                                                   "this transfer.</div>"), 400)
            return self._send(page("Transfer", "<div class='ok'>Transfer sent. Reference "
                                               "TRF-40192.</div>", user))

        if path == "/settings":
            return self._send(page("Settings", "<div class='ok'>Your changes have been "
                                               "saved.</div>", user), 200)

        if path == "/close-account":
            return self._send(page("Closed", "<div class='err'>Account closed. This action "
                                             "cannot be undone.</div>", user), 200)

        return self._send(page("Not found", "<h1>Not found</h1>", user), 404)


def free_port(start=8020, tries=30):
    for port in range(start, start + tries):
        with socket.socket() as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    raise RuntimeError("no free port")


def main():
    port = free_port()
    print("demo app on http://127.0.0.1:%d" % port)
    http.server.ThreadingHTTPServer(("127.0.0.1", port), App).serve_forever()


if __name__ == "__main__":
    main()
