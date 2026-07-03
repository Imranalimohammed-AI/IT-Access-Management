"""
Generate AccessOps project documentation PDF.
Run: python generate_pdf.py
Output: AccessOps-Project-Overview.pdf
"""

from fpdf import FPDF
from datetime import datetime

OUT = "AccessOps-Project-Overview.pdf"
PRIMARY   = (30, 64, 175)    # #1e40af
DARK      = (15, 23, 42)     # #0f172a
MUTED     = (100, 116, 139)  # #64748b
GREEN     = (22, 163, 74)    # #16a34a
AMBER     = (217, 119, 6)    # #d97706
RED       = (220, 38, 38)    # #dc2626
LIGHT_BG  = (241, 245, 249)  # #f1f5f9
WHITE     = (255, 255, 255)
BORDER    = (226, 232, 240)  # #e2e8f0
BLUE_BG   = (219, 234, 254)  # #dbeafe


class PDF(FPDF):

    def header(self):
        self.set_fill_color(*PRIMARY)
        self.rect(0, 0, 210, 14, "F")
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(*WHITE)
        self.set_y(3)
        self.cell(0, 8, "AccessOps - IT Access Management  |  Cotiviti IT Engineering", align="C")
        self.set_text_color(*DARK)
        self.ln(10)

    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(*MUTED)
        self.cell(0, 8, f"Cotiviti IT Engineering  |  Confidential  |  Generated {datetime.today().strftime('%B %d, %Y')}  |  Page {self.page_no()}", align="C")

    # -- Helpers --------------------------------------------------------------

    def h1(self, text):
        self.ln(4)
        self.set_font("Helvetica", "B", 18)
        self.set_text_color(*PRIMARY)
        self.cell(0, 10, text, ln=True)
        self.set_draw_color(*PRIMARY)
        self.set_line_width(0.6)
        self.line(self.get_x(), self.get_y(), self.get_x() + 190, self.get_y())
        self.ln(3)
        self.set_text_color(*DARK)

    def h2(self, text):
        self.ln(3)
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(*PRIMARY)
        self.cell(0, 8, text, ln=True)
        self.set_text_color(*DARK)

    def h3(self, text):
        self.ln(2)
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(*DARK)
        self.cell(0, 7, text, ln=True)

    def body(self, text, size=10):
        self.set_font("Helvetica", "", size)
        self.set_text_color(*DARK)
        self.multi_cell(0, 5.5, text)
        self.ln(1)

    def bullet(self, text, indent=8):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(*DARK)
        x = self.get_x()
        self.set_x(x + indent)
        self.set_fill_color(*PRIMARY)
        self.ellipse(x + indent - 1, self.get_y() + 2, 2, 2, "F")
        self.multi_cell(0, 5.5, "  " + text)
        self.set_x(x)

    def code(self, text):
        self.set_font("Courier", "", 9)
        self.set_fill_color(*LIGHT_BG)
        self.set_text_color(50, 50, 50)
        self.multi_cell(0, 5, "  " + text, fill=True, border=1)
        self.ln(1)
        self.set_font("Helvetica", "", 10)
        self.set_text_color(*DARK)

    def tag(self, text, color=PRIMARY, bg=BLUE_BG):
        self.set_font("Helvetica", "B", 8)
        self.set_fill_color(*bg)
        self.set_text_color(*color)
        w = self.get_string_width(text) + 6
        self.cell(w, 6, text, fill=True, border=0)
        self.set_text_color(*DARK)

    def info_box(self, title, lines, bg=LIGHT_BG, title_color=PRIMARY):
        self.set_fill_color(*bg)
        self.set_draw_color(*BORDER)
        x, y = self.get_x(), self.get_y()
        # draw box after content
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(*title_color)
        self.cell(0, 6, title, ln=True)
        self.set_font("Helvetica", "", 10)
        self.set_text_color(*DARK)
        for line in lines:
            self.set_x(x + 4)
            self.multi_cell(0, 5.5, line)
        self.ln(2)

    def section_divider(self):
        self.set_draw_color(*BORDER)
        self.set_line_width(0.3)
        self.line(self.get_x(), self.get_y(), self.get_x() + 190, self.get_y())
        self.ln(3)

    def kv_row(self, key, value, fill=False):
        self.set_fill_color(*LIGHT_BG)
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(*MUTED)
        self.cell(55, 6, key.upper(), fill=fill)
        self.set_font("Helvetica", "", 9)
        self.set_text_color(*DARK)
        self.multi_cell(0, 6, value, fill=False)

    def table(self, headers, rows, col_widths=None):
        if col_widths is None:
            col_widths = [190 // len(headers)] * len(headers)
        # Header row
        self.set_fill_color(*PRIMARY)
        self.set_text_color(*WHITE)
        self.set_font("Helvetica", "B", 9)
        for i, h in enumerate(headers):
            self.cell(col_widths[i], 7, h, border=1, fill=True)
        self.ln()
        # Data rows
        self.set_text_color(*DARK)
        for ri, row in enumerate(rows):
            self.set_fill_color(248, 250, 252) if ri % 2 == 0 else self.set_fill_color(*WHITE)
            self.set_font("Helvetica", "", 9)
            max_h = 6
            for ci, cell in enumerate(row):
                self.cell(col_widths[ci], max_h, str(cell), border=1, fill=True)
            self.ln()
        self.ln(2)

    def callout(self, icon_char, title, text, bg=(219, 234, 254), border_color=PRIMARY):
        self.set_fill_color(*bg)
        self.set_draw_color(*border_color)
        self.set_line_width(0.8)
        start_y = self.get_y()
        self.line(self.get_x(), start_y, self.get_x(), start_y + 2)  # placeholder
        self.rect(self.get_x(), self.get_y(), 190, 2, "F")  # placeholder
        x = self.get_x()
        self.set_fill_color(*bg)
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(*border_color)
        self.cell(0, 6, f"  {icon_char}  {title}", ln=True, fill=True)
        self.set_font("Helvetica", "", 10)
        self.set_text_color(*DARK)
        self.set_x(x + 8)
        self.multi_cell(182, 5.5, text, fill=False)
        self.ln(2)
        self.set_text_color(*DARK)


# -- Build PDF -----------------------------------------------------------------

pdf = PDF()
pdf.set_margins(10, 18, 10)
pdf.set_auto_page_break(auto=True, margin=16)


# ------------------------------------------------------------------------------
# PAGE 1 - Cover
# ------------------------------------------------------------------------------
pdf.add_page()

pdf.set_fill_color(*PRIMARY)
pdf.rect(0, 14, 210, 80, "F")

pdf.set_y(30)
pdf.set_font("Helvetica", "B", 32)
pdf.set_text_color(*WHITE)
pdf.cell(0, 14, "AccessOps", align="C", ln=True)

pdf.set_font("Helvetica", "", 16)
pdf.cell(0, 10, "IT Access Management Dashboard", align="C", ln=True)

pdf.set_font("Helvetica", "", 11)
pdf.set_text_color(186, 230, 253)
pdf.cell(0, 8, "Cotiviti IT Engineering  |  Internal Tool", align="C", ln=True)

pdf.set_y(100)
pdf.set_text_color(*DARK)

pdf.set_font("Helvetica", "", 11)
pdf.set_text_color(*MUTED)
pdf.cell(0, 7, f"Document prepared: {datetime.today().strftime('%B %d, %Y')}", align="C", ln=True)
pdf.cell(0, 7, "Classification: Internal / Confidential", align="C", ln=True)

pdf.ln(10)
pdf.set_font("Helvetica", "B", 12)
pdf.set_text_color(*PRIMARY)
pdf.cell(0, 7, "Project Summary", align="C", ln=True)
pdf.set_draw_color(*BORDER)
pdf.line(40, pdf.get_y(), 170, pdf.get_y())
pdf.ln(4)

pdf.set_font("Helvetica", "", 10)
pdf.set_text_color(*DARK)
summary = (
    "AccessOps is a web-based Identity & Access Management (IAM) dashboard built for Cotiviti IT "
    "administrators. It provides real-time visibility into user access across Okta SSO and Active "
    "Directory, with built-in approval workflows, tamper-evident audit logging, bulk offboarding, "
    "and a Ticket Distribution module for shift-based helpdesk operations.\n\n"
    "The system integrates directly with the Okta REST API and Active Directory via LDAP, using "
    "API keys and service account credentials managed securely through environment variables. "
    "All credentials are loaded at runtime and never hardcoded into source files."
)
pdf.multi_cell(0, 5.5, summary)

pdf.ln(6)
pdf.set_fill_color(*LIGHT_BG)
pdf.set_draw_color(*BORDER)

stats = [
    ("Tech Stack", "Python 3.14 + Flask 3.0  |  Vanilla HTML/CSS/JS  |  Okta API v1  |  LDAP3 (NTLM)"),
    ("Port", "5050  (configurable via FLASK_PORT)"),
    ("Data Storage", "Append-only JSONL files  (audit_log, access_requests, offboarded_users)"),
    ("Authentication", "Okta SSWS token  +  AD NTLM service account  (both via .env)"),
    ("File", "it-access-dashboard.html  +  main.py  +  .env"),
]
for k, v in stats:
    pdf.kv_row(k, v, fill=True)
    pdf.ln(1)


# ------------------------------------------------------------------------------
# PAGE 2 - API Key Architecture (MAIN FOCUS)
# ------------------------------------------------------------------------------
pdf.add_page()
pdf.h1("How API Keys Are Used")

pdf.body(
    "AccessOps relies on two sets of credentials to connect to external systems: an Okta API token "
    "for SSO and identity management, and an Active Directory service account for LDAP operations. "
    "Neither credential is ever hardcoded. Both are loaded exclusively from environment variables "
    "at server startup via python-dotenv."
)

# -- .env structure ------------------------------------------------
pdf.h2("1.  The .env File - Where Credentials Live")
pdf.body("All credentials are stored in a single .env file in the project root. This file is never committed to source control.")

pdf.set_font("Courier", "", 9)
pdf.set_fill_color(*LIGHT_BG)
pdf.set_draw_color(*BORDER)
env_lines = [
    "# Okta",
    "OKTA_DOMAIN=cotiviti.okta.com",
    "OKTA_API_TOKEN=ssws_00xxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "",
    "# Active Directory",
    "AD_SERVER=ldap://ad.cotiviti.com",
    "AD_DOMAIN=cotiviti.com",
    "AD_BIND_USER=svc-accessops@cotiviti.com",
    "AD_BIND_PASSWORD=--------------",
    "",
    "# App config",
    "FLASK_PORT=5050",
    "FLASK_DEBUG=false",
]
for line in env_lines:
    color = MUTED if line.startswith("#") or line == "" else (50, 50, 50)
    pdf.set_text_color(*color)
    pdf.cell(0, 5, "  " + line, ln=True)
pdf.set_text_color(*DARK)
pdf.ln(2)

# -- How they are loaded --------------------------------------------
pdf.h2("2.  Loading Credentials at Startup  (main.py)")
pdf.body(
    "When main.py starts, python-dotenv reads the .env file and injects all variables into the "
    "process environment. The app then reads each variable using os.environ.get():"
)
pdf.code(
    "load_dotenv()                                    # reads .env into os.environ\n"
    "\n"
    "OKTA_DOMAIN    = os.environ.get('OKTA_DOMAIN', '')    # e.g. cotiviti.okta.com\n"
    "OKTA_API_TOKEN = os.environ.get('OKTA_API_TOKEN', '') # SSWS token\n"
    "AD_SERVER      = os.environ.get('AD_SERVER', '')      # ldap://...\n"
    "AD_BIND_USER   = os.environ.get('AD_BIND_USER', '')   # service account UPN\n"
    "AD_BIND_PASS   = os.environ.get('AD_BIND_PASSWORD', '')"
)
pdf.body(
    "If any required credential is missing the app logs a warning on startup but continues running. "
    "The first API call that needs the missing credential will return a 500 error with a clear "
    "message - it never silently fails."
)

# -- Okta API token ------------------------------------------------
pdf.h2("3.  Okta API Token - How It Is Used")
pdf.body(
    "Every call to the Okta REST API attaches the token in an Authorization header using Okta's "
    "SSWS (Session Web Service) scheme. A helper function builds this header once and reuses it:"
)
pdf.code(
    "def _okta_headers() -> dict:\n"
    "    if not OKTA_API_TOKEN:\n"
    "        raise RuntimeError('OKTA_API_TOKEN not set in environment.')\n"
    "    return {\n"
    "        'Authorization': f'SSWS {OKTA_API_TOKEN}',\n"
    "        'Accept':        'application/json',\n"
    "        'Content-Type':  'application/json',\n"
    "    }"
)

pdf.table(
    ["Okta Action", "HTTP Method", "Endpoint Called", "Token Required"],
    [
        ["Look up user by email",  "GET",    "/api/v1/users^filter=profile.email eq ...", "Yes"],
        ["Get user groups",        "GET",    "/api/v1/users/{id}/groups",                 "Yes"],
        ["Get app assignments",    "GET",    "/api/v1/users/{id}/appLinks",               "Yes"],
        ["Suspend account",        "POST",   "/api/v1/users/{id}/lifecycle/suspend",      "Yes"],
        ["Reactivate account",     "POST",   "/api/v1/users/{id}/lifecycle/activate",     "Yes"],
        ["Reset MFA factors",      "POST",   "/api/v1/users/{id}/lifecycle/reset_factors","Yes"],
        ["Reset password",         "POST",   "/api/v1/users/{id}/lifecycle/reset_password","Yes"],
        ["Remove app assignment",  "DELETE", "/api/v1/apps/{app_id}/users/{user_id}",     "Yes"],
    ],
    col_widths=[55, 22, 88, 25],
)


# ------------------------------------------------------------------------------
# PAGE 3 - AD credentials + Security model
# ------------------------------------------------------------------------------
pdf.add_page()
pdf.h1("API Keys & Credentials - Continued")

# -- AD credentials ------------------------------------------------
pdf.h2("4.  Active Directory Service Account")
pdf.body(
    "Active Directory is accessed via LDAP using the ldap3 library with NTLM authentication. "
    "The service account credentials (AD_BIND_USER and AD_BIND_PASSWORD) are passed directly "
    "from the environment to the ldap3 Connection object:"
)
pdf.code(
    "def _ad_connect():\n"
    "    from ldap3 import Server, Connection, ALL, NTLM\n"
    "    server = Server(AD_SERVER, get_info=ALL)\n"
    "    conn   = Connection(\n"
    "        server,\n"
    "        user=AD_BIND_USER,       # loaded from AD_BIND_USER in .env\n"
    "        password=AD_BIND_PASS,   # loaded from AD_BIND_PASSWORD in .env\n"
    "        authentication=NTLM,\n"
    "        auto_bind=True\n"
    "    )\n"
    "    return conn"
)

pdf.table(
    ["AD Operation", "LDAP Action", "Credential Used"],
    [
        ["Look up user by email",     "SEARCH  (mail=email)",               "AD_BIND_USER + AD_BIND_PASSWORD"],
        ["Disable AD account",        "MODIFY userAccountControl (bit 0x2)","AD_BIND_USER + AD_BIND_PASSWORD"],
        ["Remove from security group","MODIFY group.member (MODIFY_DELETE)", "AD_BIND_USER + AD_BIND_PASSWORD"],
    ],
    col_widths=[60, 75, 55],
)

# -- Credential flow diagram ----------------------------------------
pdf.h2("5.  End-to-End Credential Flow")
pdf.set_font("Courier", "", 9)
pdf.set_fill_color(*LIGHT_BG)
pdf.set_text_color(50, 50, 50)
flow = [
    ".env file",
    "    -",
    "    -  python-dotenv (load_dotenv)",
    "    -",
    "os.environ  --- OKTA_API_TOKEN  ---  _okta_headers()  ---  Authorization: SSWS <token>",
    "            --- AD_BIND_USER    ---  _ad_connect()    ---  NTLM bind to AD server",
    "            --- AD_BIND_PASS    ---  _ad_connect()    ---  NTLM bind to AD server",
    "    -",
    "    -  Credentials never reach the browser",
    "    -  API responses contain user data only - no tokens, no passwords",
    "    -",
    "Frontend (it-access-dashboard.html)  ---  JSON response  --  Flask route",
]
for line in flow:
    pdf.cell(0, 5, "  " + line, ln=True)
pdf.set_text_color(*DARK)
pdf.ln(3)

# -- Security model ------------------------------------------------
pdf.h2("6.  Security Design for API Keys")

pdf.table(
    ["Security Control", "How It Is Applied"],
    [
        ["No hardcoded secrets",      "All tokens/passwords read from os.environ - zero credentials in source code"],
        ["Token never sent to browser","Flask routes return JSON data only - the OKTA_API_TOKEN is server-side only"],
        ["Credential validation",     "Startup logs warn if OKTA_DOMAIN or OKTA_API_TOKEN is missing"],
        ["Scoped Okta token",         "Token should have read + lifecycle scopes only - not super-admin"],
        ["Minimal AD permissions",    "Service account has read + targeted modify only - not domain admin"],
        ["SSWS auth scheme",          "Okta SSWS tokens are revocable and auditable in the Okta Admin Console"],
        [".env not committed",        ".env listed in .gitignore - .env.example provided as safe template"],
        ["NTLM over LDAP",            "AD password never transmitted in plaintext - NTLM challenge-response"],
    ],
    col_widths=[70, 120],
)

pdf.callout(
    "!",
    "Important: Rotating API Keys",
    "If the OKTA_API_TOKEN is rotated or an AD service account password changes, update the .env "
    "file and restart the Flask server (python main.py). No code changes are needed - the new "
    "value is picked up automatically on next startup via load_dotenv().",
    bg=(254, 243, 199),
    border_color=AMBER,
)


# ------------------------------------------------------------------------------
# PAGE 4 - Features & Architecture
# ------------------------------------------------------------------------------
pdf.add_page()
pdf.h1("Features & Architecture")

pdf.h2("Module Overview")
pdf.table(
    ["Module", "What It Does", "Uses API Key^"],
    [
        ["Users",               "Search users, view Okta profile, AD account, app access, licenses", "Yes - Okta + AD"],
        ["Applications",        "All application assignments across the org",                         "Yes - Okta"],
        ["Licenses",            "Microsoft 365 and software license management",                      "Yes - Okta"],
        ["Requests",            "Approve or deny access requests",                                    "Yes - Okta"],
        ["Audit Log",           "Tamper-evident log of every IAM action",                             "Stored locally"],
        ["Agent View",          "Side-by-side user comparison with risk flags",                       "Yes - Okta + AD"],
        ["Bulk Offboarding",    "CSV upload - review - execute for multiple users",                   "Yes - Okta + AD"],
        ["Ticket Distribution", "Assign helpdesk tickets to agents by shift and specialization",      "Client-side only"],
    ],
    col_widths=[38, 105, 47],
)

pdf.h2("System Architecture")
pdf.set_font("Courier", "", 9)
pdf.set_fill_color(*LIGHT_BG)
pdf.set_text_color(50, 50, 50)
arch = [
    "Browser  (it-access-dashboard.html)",
    "    -",
    "    -   REST API calls  fetch('/api/...')",
    "    -",
    "Flask Backend  (main.py)  :5050",
    "    -",
    "    --- Okta REST API  (HTTPS + SSWS token)  --  cotiviti.okta.com",
    "    --- Active Directory  (LDAP/NTLM)         --  ad.cotiviti.com",
    "    --- Local data/  (JSONL files)",
    "            --- audit_log.jsonl",
    "            --- access_requests.jsonl",
    "            --- offboarded_users.jsonl",
]
for line in arch:
    pdf.cell(0, 5, "  " + line, ln=True)
pdf.set_text_color(*DARK)
pdf.ln(3)

pdf.h2("Project Files")
pdf.table(
    ["File", "Extension", "Purpose"],
    [
        ["it-access-dashboard", ".html", "Single-page frontend - all UI, CSS and client-side JS"],
        ["main",                ".py",   "Flask REST API server - all backend logic and integrations"],
        ["README",              ".md",   "Setup instructions, API endpoints, CSV format reference"],
        ["ARCHITECTURE",        ".md",   "System design, component map, data flow diagrams"],
        ["requirements",        ".txt",  "Pinned Python package versions for reproducible installs"],
        ["requirements",        ".in",   "Source dependency list (used to regenerate requirements.txt)"],
        [".env",                ".env",  "Runtime credentials - OKTA_API_TOKEN, AD_BIND_PASSWORD, etc."],
    ],
    col_widths=[48, 22, 120],
)


# ------------------------------------------------------------------------------
# PAGE 5 - Setup, API Endpoints, Production notes
# ------------------------------------------------------------------------------
pdf.add_page()
pdf.h1("Setup & API Reference")

pdf.h2("Getting Started")
steps = [
    ("1", "Create virtual environment", "uv venv .venv"),
    ("2", "Activate venv",              ".venv\\Scripts\\Activate.ps1"),
    ("3", "Install dependencies",       "uv pip install -r requirements.txt"),
    ("4", "Configure credentials",      "Edit .env - add OKTA_API_TOKEN, AD_BIND_USER, AD_BIND_PASSWORD"),
    ("5", "Start the server",           "python main.py"),
    ("6", "Open in browser",            "http://localhost:5050"),
]
pdf.set_font("Helvetica", "", 10)
for num, label, cmd in steps:
    pdf.set_fill_color(*PRIMARY)
    pdf.set_text_color(*WHITE)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(8, 6, num, fill=True, align="C")
    pdf.set_text_color(*DARK)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(60, 6, "  " + label)
    pdf.set_font("Courier", "", 9)
    pdf.set_text_color(50, 80, 150)
    pdf.cell(0, 6, cmd, ln=True)
    pdf.set_text_color(*DARK)
pdf.ln(3)

pdf.h2("API Endpoints")
pdf.table(
    ["Method", "Endpoint", "Description", "Auth"],
    [
        ["GET",    "/api/okta/user^email=",           "Fetch Okta profile + groups + apps",        "SSWS token"],
        ["GET",    "/api/ad/user^email=",              "Fetch AD account + group memberships",      "NTLM"],
        ["POST",   "/api/okta/user/{id}/suspend",      "Suspend Okta account",                      "SSWS token"],
        ["POST",   "/api/okta/user/{id}/activate",     "Reactivate Okta account",                   "SSWS token"],
        ["POST",   "/api/okta/user/{id}/reset-mfa",    "Clear all MFA factors",                     "SSWS token"],
        ["POST",   "/api/okta/user/{id}/reset-password","Send password reset email",                "SSWS token"],
        ["POST",   "/api/okta/user/{id}/remove-app",   "Remove app assignment",                     "SSWS token"],
        ["POST",   "/api/ad/user/disable",             "Disable AD account (UAC bit 0x2)",          "NTLM"],
        ["POST",   "/api/ad/user/remove-group",        "Remove user from AD security group",        "NTLM"],
        ["GET",    "/api/requests",                    "List all access requests",                  "None"],
        ["POST",   "/api/requests",                    "Submit a new access request",               "None"],
        ["POST",   "/api/requests/{id}/approve",       "Approve request",                           "None"],
        ["POST",   "/api/requests/{id}/deny",          "Deny request",                              "None"],
        ["POST",   "/api/offboard/preview",            "Parse CSV, return preview",                 "SSWS + NTLM"],
        ["POST",   "/api/offboard/execute",            "Execute bulk offboarding",                  "SSWS + NTLM"],
        ["GET",    "/api/offboard/history",            "View past offboarding records",             "None"],
        ["GET",    "/api/audit",                       "Retrieve last 200 audit entries",           "None"],
        ["GET",    "/api/health",                      "Okta + AD connectivity status",             "SSWS + NTLM"],
    ],
    col_widths=[16, 68, 72, 34],
)

pdf.h2("Production Hardening Checklist")
items = [
    "Run behind nginx reverse proxy with HTTPS/TLS",
    "Add authentication to Flask app (Okta SSO or Basic Auth) - currently open internally",
    "Restrict CORS from wildcard (*) to your internal domain only",
    "Move JSONL data files to PostgreSQL or SQLite for reliability",
    "Add flask-limiter rate limiting to all POST endpoints",
    "Use a dedicated Okta API token with minimum required scopes (not super-admin)",
    "Use an AD service account with read + targeted modify permissions only",
    "Store .env secrets in a secrets manager (Vault, AWS Secrets Manager) in production",
    "Rotate OKTA_API_TOKEN and AD_BIND_PASSWORD on a regular schedule",
]
for item in items:
    pdf.bullet(item)

pdf.ln(4)
pdf.set_fill_color(*LIGHT_BG)
pdf.set_draw_color(*BORDER)
pdf.set_font("Helvetica", "I", 9)
pdf.set_text_color(*MUTED)
pdf.multi_cell(
    0, 5,
    "This document was auto-generated from the AccessOps source files. "
    "For the latest information refer to README.md and ARCHITECTURE.md in the project folder.",
    border=1, fill=True
)

# -- Save ----------------------------------------------------------
pdf.output(OUT)
print(f"PDF created: {OUT}")
